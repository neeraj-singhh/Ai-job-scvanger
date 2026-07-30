"""
Background scheduler.

Runs the full ingestion pipeline (fetch -> normalize -> embed -> save ->
match -> notify) on a fixed interval using APScheduler's async executor.
For higher-throughput deployments, swap this for Celery + a broker
(Redis/RabbitMQ) without changing PipelineService itself.
"""
from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.ai.provider import get_ai_provider
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import db_session_ctx
from app.services.pipeline_service import PipelineService

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


async def run_pipeline_job() -> None:
    """The actual job body executed on each scheduler tick."""
    settings = get_settings()
    logger.info("Scheduled pipeline run starting")
    try:
        ai_provider = get_ai_provider()
        async with db_session_ctx() as db:
            pipeline = PipelineService(db=db, ai_provider=ai_provider, settings=settings)
            await pipeline.run_full_pipeline()
    except Exception:  # noqa: BLE001
        logger.exception("Scheduled pipeline run failed")


def start_scheduler() -> None:
    settings = get_settings()
    if scheduler.running:
        return

    scheduler.add_job(
        run_pipeline_job,
        trigger=IntervalTrigger(hours=settings.SCRAPE_INTERVAL_HOURS),
        id="job_ingestion_pipeline",
        replace_existing=True,
        # Run once shortly after startup too, so the app isn't empty for hours.
        next_run_time=None,
    )
    scheduler.start()
    logger.info("Scheduler started: pipeline runs every %sh", settings.SCRAPE_INTERVAL_HOURS)


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
