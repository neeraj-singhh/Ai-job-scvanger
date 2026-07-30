"""
Centralized logging configuration.

Uses structured (JSON-capable) logging so logs are easy to ship to
Railway/Render/DigitalOcean log drains or a proper log aggregator later.
"""
import logging
import sys

from app.core.config import get_settings


class RequestContextFilter(logging.Filter):
    """Placeholder filter so request-scoped fields (request_id, user_id)
    can be injected by middleware later without changing this config."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "user_id"):
            record.user_id = "-"
        return True


def configure_logging() -> None:
    settings = get_settings()
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | req=%(request_id)s user=%(user_id)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy third-party loggers unless we're in DEBUG
    for noisy in ("httpx", "httpcore", "apscheduler", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(level if settings.DEBUG else logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
