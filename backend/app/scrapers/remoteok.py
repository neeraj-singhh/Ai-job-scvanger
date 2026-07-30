"""
RemoteOK scraper.

RemoteOK exposes a public JSON feed at https://remoteok.com/api which
makes it a good first/reference provider — no HTML scraping needed.
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.logging import get_logger
from app.scrapers.base import BaseScraper, RawJob, ScraperError

logger = get_logger(__name__)

REMOTEOK_API_URL = "https://remoteok.com/api"


class RemoteOKScraper(BaseScraper):
    source_name = "remoteok"

    async def fetch(self) -> list[RawJob]:
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.get(REMOTEOK_API_URL, headers=headers)
                resp.raise_for_status()
                payload = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ScraperError(f"RemoteOK fetch failed: {exc}") from exc

        jobs: list[RawJob] = []
        for entry in payload:
            # RemoteOK's feed prepends a legend/metadata object with no "id" field.
            if not isinstance(entry, dict) or "id" not in entry:
                continue
            try:
                jobs.append(self._parse_entry(entry))
            except Exception as exc:  # noqa: BLE001 - one bad listing shouldn't kill the batch
                logger.warning("Skipping malformed RemoteOK entry %s: %s", entry.get("id"), exc)
                continue

        logger.info("RemoteOK: fetched %d jobs", len(jobs))
        return jobs

    def _parse_entry(self, entry: dict) -> RawJob:
        posted_at = None
        if epoch := entry.get("epoch"):
            posted_at = datetime.fromtimestamp(epoch, tz=timezone.utc)

        salary_min = entry.get("salary_min")
        salary_max = entry.get("salary_max")
        salary_text = None
        if salary_min or salary_max:
            salary_text = f"{salary_min or ''}-{salary_max or ''} USD"

        return RawJob(
            source=self.source_name,
            source_job_id=str(entry["id"]),
            source_url=entry.get("url") or f"https://remoteok.com/remote-jobs/{entry['id']}",
            title=entry.get("position", "Unknown Title"),
            company=entry.get("company", "Unknown Company"),
            raw_description_html=entry.get("description", ""),
            location_text=entry.get("location") or "Remote",
            salary_text=salary_text,
            employment_type_text=None,  # RemoteOK doesn't reliably expose this; AI normalization infers it
            posted_at=posted_at,
            extra={"tags": entry.get("tags", [])},
        )
