from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.job import Job
from app.models.matching import JobMatch, SavedJob
from app.schemas.job import JobListParams, SavedJobRequest


class JobService:
    """Repository-style service for reading jobs and managing saved jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_jobs(self, params: JobListParams) -> tuple[list[Job], int]:
        stmt = select(Job).where(Job.is_active.is_(True))

        if params.query:
            like = f"%{params.query}%"
            stmt = stmt.where(or_(Job.title.ilike(like), Job.company.ilike(like)))
        if params.location:
            stmt = stmt.where(Job.location.ilike(f"%{params.location}%"))
        if params.remote_only:
            stmt = stmt.where(Job.remote.is_(True))
        if params.employment_type:
            stmt = stmt.where(Job.employment_type == params.employment_type)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            stmt.order_by(Job.created_at.desc())
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )
        jobs = (await self.db.execute(stmt)).scalars().all()
        return list(jobs), total

    async def get_job(self, job_id: uuid.UUID) -> Job:
        job = await self.db.get(Job, job_id)
        if job is None:
            raise NotFoundError("Job not found")
        return job

    async def get_matches_for_profile(self, profile_id: uuid.UUID, min_score: float = 0.0) -> list[JobMatch]:
        stmt = (
            select(JobMatch)
            .options(joinedload(JobMatch.job))
            .where(JobMatch.profile_id == profile_id, JobMatch.score >= min_score)
            .order_by(JobMatch.score.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def save_job(self, profile_id: uuid.UUID, payload: SavedJobRequest) -> SavedJob:
        await self.get_job(payload.job_id)  # raises NotFoundError if missing

        existing = await self.db.execute(
            select(SavedJob).where(
                SavedJob.profile_id == profile_id, SavedJob.job_id == payload.job_id
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError("Job already saved")

        saved = SavedJob(profile_id=profile_id, job_id=payload.job_id, notes=payload.notes)
        self.db.add(saved)
        await self.db.commit()
        await self.db.refresh(saved)
        return saved

    async def list_saved_jobs(self, profile_id: uuid.UUID) -> list[SavedJob]:
        stmt = (
            select(SavedJob)
            .options(joinedload(SavedJob.job))
            .where(SavedJob.profile_id == profile_id)
            .order_by(SavedJob.created_at.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def delete_saved_job(self, profile_id: uuid.UUID, job_id: uuid.UUID) -> None:
        stmt = select(SavedJob).where(
            SavedJob.profile_id == profile_id, SavedJob.job_id == job_id
        )
        saved = (await self.db.execute(stmt)).scalar_one_or_none()
        if saved is None:
            raise NotFoundError("Saved job not found")
        await self.db.delete(saved)
        await self.db.commit()
