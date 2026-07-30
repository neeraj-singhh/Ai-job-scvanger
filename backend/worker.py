"""
Standalone worker entrypoint.

Runs ONLY the scheduler (no HTTP server). Use this in production when
you're horizontally scaling the API (multiple uvicorn instances) and
need exactly one process running the ingestion pipeline on a timer.

Run with:
    python worker.py
"""
import asyncio
import signal

from app.core.logging import configure_logging, get_logger
from app.scheduler.jobs import scheduler, shutdown_scheduler, start_scheduler

configure_logging()
logger = get_logger(__name__)


async def main() -> None:
    start_scheduler()
    logger.info("Worker process started. Waiting for scheduled runs...")

    stop_event = asyncio.Event()

    def _handle_stop(*_args):
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_stop)

    await stop_event.wait()
    shutdown_scheduler()
    logger.info("Worker process stopped.")


if __name__ == "__main__":
    asyncio.run(main())
