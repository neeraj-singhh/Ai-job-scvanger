"""
Greenhouse scraper.

Greenhouse exposes a public per-company job board JSON API:
    https://boards-api.greenhouse.io/v1/boards/<board_token>/jobs?content=true

Since Greenhouse is multi-tenant (one board per company), this scraper
is configured with a list of company board tokens rather than a single
fixed endpoint. Configure via `GREENHOUSE_BOARD_TOKENS` env var
(comma-separated), e.g. "stripe,figma,notion".
"""
from __future__ import annotations

import os

import httpx

from app.core.logging import get_logger
from app.scrapers.base import BaseScraper, RawJob, ScraperError

logger = get_logger(__name__)

GREENHOUSE_BOARD_API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


class GreenhouseScraper(BaseScraper):
    source_name = "greenhouse"

    def __init__(self, *, board_tokens: list[str] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.board_tokens = board_tokens or self._tokens_from_env()

    @staticmethod
    def _tokens_from_env() -> list[str]:
        raw = os.getenv("GREENHOUSE_BOARD_TOKENS", "")
        return [t.strip() for t in raw.split(",") if t.strip()]

    async def fetch(self) -> list[RawJob]:
        if not self.board_tokens:
            logger.info("Greenhouse: no board tokens configured, skipping")
            return []

        all_jobs: list[RawJob] = []
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for token in self.board_tokens:
                try:
                    all_jobs.extend(await self._fetch_board(client, token))
                except ScraperError as exc:
                    logger.warning("Greenhouse: board '%s' failed: %s", token, exc)
                    continue

        logger.info("Greenhouse: fetched %d jobs across %d boards", len(all_jobs), len(self.board_tokens))
        return all_jobs

    async def _fetch_board(self, client: httpx.AsyncClient, token: str) -> list[RawJob]:
        url = GREENHOUSE_BOARD_API.format(token=token)
        headers = {"User-Agent": self.user_agent}
        try:
            resp = await client.get(url, headers=headers, params={"content": "true"})
            resp.raise_for_status()
            payload = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ScraperError(f"Greenhouse board '{token}' fetch failed: {exc}") from exc

        jobs: list[RawJob] = []
        for entry in payload.get("jobs", []):
            try:
                jobs.append(self._parse_entry(entry, board_token=token))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping malformed Greenhouse entry %s: %s", entry.get("id"), exc)
        return jobs

    def _parse_entry(self, entry: dict, board_token: str) -> RawJob:
        location = None
        if loc := entry.get("location"):
            location = loc.get("name")

        return RawJob(
            source=self.source_name,
            source_job_id=str(entry["id"]),
            source_url=entry.get("absolute_url", ""),
            title=entry.get("title", "Unknown Title"),
            company=board_token,
            raw_description_html=entry.get("content", ""),
            location_text=location,
            salary_text=None,  # Greenhouse rarely includes salary in the public API
            employment_type_text=None,
            posted_at=None,
            extra={"board_token": board_token, "departments": entry.get("departments", [])},
        )
