"""
Scraper registry.

This is the single place new provider plugins get wired in. The
scheduler and pipeline never import a specific scraper class directly —
they iterate `get_enabled_scrapers()`. Adding provider #11 means adding
one line here (plus the scraper file itself).
"""
from __future__ import annotations

from app.core.config import get_settings
from app.scrapers.base import BaseScraper
from app.scrapers.greenhouse import GreenhouseScraper
from app.scrapers.remoteok import RemoteOKScraper

# --- Register every available scraper class here ---
AVAILABLE_SCRAPERS: dict[str, type[BaseScraper]] = {
    "remoteok": RemoteOKScraper,
    "greenhouse": GreenhouseScraper,
    # "lever": LeverScraper,          # TODO: next increment
    # "ashby": AshbyScraper,          # TODO: next increment
    # "wellfound": WellfoundScraper,  # TODO: next increment
}


def get_enabled_scrapers() -> list[BaseScraper]:
    """
    Instantiate every registered scraper. Individual scrapers are
    responsible for no-op'ing themselves (see GreenhouseScraper) if
    they're not configured (e.g. missing API keys/tokens), so this
    function doesn't need an explicit enable/disable list.
    """
    settings = get_settings()
    instances: list[BaseScraper] = []
    for name, scraper_cls in AVAILABLE_SCRAPERS.items():
        instances.append(
            scraper_cls(
                timeout_seconds=settings.SCRAPER_REQUEST_TIMEOUT_SECONDS,
                user_agent=settings.SCRAPER_USER_AGENT,
            )
        )
    return instances
