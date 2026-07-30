"""
Scraper plugin contract.

Every job source (Greenhouse, Lever, Ashby, RemoteOK, a scraped career
page, etc.) is implemented as a subclass of `BaseScraper` and returns a
list of `RawJob` objects — a common, source-agnostic shape. The AI
normalization layer (app/ai/normalizer.py) is what later turns these
loosely-structured `RawJob`s into fully structured `Job` rows.

To add a new provider:
    1. Create `app/scrapers/<provider>.py`
    2. Subclass `BaseScraper`, implement `fetch()`
    3. Register it in `app/scrapers/registry.py`

No other code needs to change — the scheduler and pipeline discover
scrapers via the registry.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawJob:
    """
    Source-agnostic representation of a scraped job posting, *before*
    AI normalization. Fields are intentionally loose (raw strings) since
    every provider formats things differently (e.g. salary as "$120k-$150k"
    vs "120000-150000 USD").
    """

    source: str                    # e.g. "greenhouse", "lever", "remoteok"
    source_job_id: str             # provider-native unique id
    source_url: str
    title: str
    company: str
    raw_description_html: str      # unmodified HTML/markdown/text from the source
    location_text: str | None = None
    salary_text: str | None = None
    employment_type_text: str | None = None
    posted_at: datetime | None = None
    extra: dict = field(default_factory=dict)  # any provider-specific metadata worth keeping


class ScraperError(Exception):
    """Raised when a scraper fails to fetch or parse jobs from its source."""


class BaseScraper(abc.ABC):
    """All job source plugins must implement this interface."""

    #: Unique, stable identifier for this source. Used as `Job.source` and
    #: for dedup keys, so it must never change once jobs have been ingested.
    source_name: str

    def __init__(self, *, timeout_seconds: int = 20, user_agent: str = "AIJobScavengerBot/1.0"):
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    @abc.abstractmethod
    async def fetch(self) -> list[RawJob]:
        """Fetch and return all currently-listed jobs from this source.

        Implementations should:
          - Be resilient to partial failures (skip a malformed listing, don't crash the run)
          - Respect the source's rate limits / robots.txt
          - Raise `ScraperError` on unrecoverable failures so the pipeline can log + continue
        """
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Optional lightweight check that the source is reachable. Default: assume healthy."""
        return True
