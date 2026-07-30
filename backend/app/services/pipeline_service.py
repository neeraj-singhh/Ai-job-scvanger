"""
Ingestion pipeline orchestration.

    fetch jobs -> normalize (AI) -> generate embeddings -> save jobs
        -> match users -> store matches -> queue notifications

This is invoked by the scheduler (app/scheduler/jobs.py) on a fixed
interval, and could equally be triggered manually via an admin endpoint.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.normalizer import JobNormalizer
from app.ai.provider import AIProvider
from app.core.config import Settings
from app.core.logging import get_logger
from app.matcher.engine import score_match
from app.models.job import Job
from app.models.matching import JobMatch, NotificationHistory, NotificationType
from app.models.preference import Preference
from app.scrapers.base import RawJob, ScraperError
from app.scrapers.registry import get_enabled_scrapers

logger = get_logger(__name__)


class PipelineService:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider, settings: Settings):
        self.db = db
        self.ai_provider = ai_provider
        self.settings = settings
        self.normalizer = JobNormalizer(ai_provider)

    async def run_full_pipeline(self) -> dict:
        """Runs one full ingestion + matching cycle. Returns a summary dict for logging/metrics."""
        raw_jobs = await self._fetch_all_sources()
        saved_jobs = await self._normalize_and_save(raw_jobs)
        match_count = await self._match_all_profiles(saved_jobs)
        notified_count = await self._queue_notifications()

        summary = {
            "raw_jobs_fetched": len(raw_jobs),
            "jobs_saved_or_updated": len(saved_jobs),
            "new_matches": match_count,
            "notifications_queued": notified_count,
        }
        logger.info("Pipeline run complete: %s", summary)
        return summary

    # --- Step 1: fetch ---
    async def _fetch_all_sources(self) -> list[RawJob]:
        raw_jobs: list[RawJob] = []
        for scraper in get_enabled_scrapers():
            try:
                jobs = await scraper.fetch()
                raw_jobs.extend(jobs)
            except ScraperError as exc:
                logger.error("Scraper '%s' failed: %s", scraper.source_name, exc)
                continue
        return raw_jobs

    # --- Step 2-4: normalize, embed, save (dedup by source + source_job_id) ---
    async def _normalize_and_save(self, raw_jobs: list[RawJob]) -> list[Job]:
        saved: list[Job] = []

        for raw in raw_jobs:
            existing = await self.db.execute(
                select(Job).where(Job.source == raw.source, Job.source_job_id == raw.source_job_id)
            )
            job = existing.scalar_one_or_none()
            if job is not None:
                # Already ingested; skip re-normalizing to save AI spend.
                # (A future increment can add re-normalization on content hash change.)
                continue

            normalized = await self.normalizer.normalize(raw)
            embedding_text = (
                f"{normalized.title}\n{normalized.description}\n"
                f"Skills: {', '.join(normalized.required_skills)}"
            )
            embedding = await self.ai_provider.embed(embedding_text)

            job = Job(
                source=raw.source,
                source_job_id=raw.source_job_id,
                source_url=raw.source_url,
                title=normalized.title,
                company=normalized.company,
                location=normalized.location,
                remote=normalized.remote,
                salary_min=normalized.salary_min,
                salary_max=normalized.salary_max,
                salary_currency=normalized.salary_currency,
                experience_level=normalized.experience_level,
                employment_type=normalized.employment_type,
                required_skills=normalized.required_skills,
                responsibilities=normalized.responsibilities,
                benefits=normalized.benefits,
                description_raw=raw.raw_description_html,
                description_normalized=normalized.description,
                embedding=embedding,
            )
            self.db.add(job)
            saved.append(job)

        if saved:
            await self.db.commit()
            for job in saved:
                await self.db.refresh(job)

        return saved

    # --- Step 5-6: match every profile against newly saved jobs, store matches ---
    async def _match_all_profiles(self, jobs: list[Job]) -> int:
        if not jobs:
            return 0

        preferences = list((await self.db.execute(select(Preference))).scalars().all())
        new_match_count = 0

        for preference in preferences:
            for job in jobs:
                result = score_match(preference, job)
                if result is None or result.score < self.settings.MATCH_MIN_SCORE:
                    continue

                existing = await self.db.execute(
                    select(JobMatch).where(
                        JobMatch.profile_id == preference.profile_id, JobMatch.job_id == job.id
                    )
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                self.db.add(
                    JobMatch(
                        profile_id=preference.profile_id,
                        job_id=job.id,
                        score=result.score,
                        matched_skills=result.matched_skills,
                        missing_skills=result.missing_skills,
                        explanation=result.explanation,
                    )
                )
                new_match_count += 1

        if new_match_count:
            await self.db.commit()

        return new_match_count

    # --- Step 7: queue notifications for un-notified matches ---
    async def _queue_notifications(self) -> int:
        if not self.settings.NOTIFICATIONS_ENABLED:
            return 0

        stmt = select(JobMatch).where(JobMatch.notified.is_(False))
        pending_matches = list((await self.db.execute(stmt)).scalars().all())

        for match in pending_matches:
            job = await self.db.get(Job, match.job_id)
            if job is None:
                continue
            self.db.add(
                NotificationHistory(
                    profile_id=match.profile_id,
                    job_match_id=match.id,
                    type=NotificationType.new_match,
                    title=f"New match: {job.title} at {job.company}",
                    body=f"{round(match.score * 100)}% match \u2014 {job.title} at {job.company}",
                )
            )
            match.notified = True

        if pending_matches:
            await self.db.commit()

        return len(pending_matches)
