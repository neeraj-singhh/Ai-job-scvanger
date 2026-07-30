"""
FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000

Run in production (see docker/Dockerfile.backend):
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.scheduler.jobs import shutdown_scheduler, start_scheduler

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (%s)", settings.APP_NAME, settings.ENVIRONMENT)
    # RUN_SCHEDULER_IN_PROCESS defaults to true for single-instance/dev setups.
    # For multi-instance production deploys, run the scheduler as its own
    # service (see docker/Dockerfile.worker) and set this to false on the
    # API instances to avoid duplicate scrape/match runs.
    if settings.RUN_SCHEDULER_IN_PROCESS:
        start_scheduler()
    yield
    if settings.RUN_SCHEDULER_IN_PROCESS:
        shutdown_scheduler()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "environment": settings.ENVIRONMENT}
