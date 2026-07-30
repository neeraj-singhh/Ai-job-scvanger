"""
Application configuration.

All configuration is loaded from environment variables. Never hardcode
secrets here. See `.env.example` at the repo root for the full list of
variables this application expects.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "AI Job Scavenger"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    DEBUG: bool = Field(default=False)
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str = Field(..., description="Used to sign internal JWTs / session tokens")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # --- CORS ---
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "app://."])

    # --- Supabase ---
    SUPABASE_URL: str = Field(..., description="https://<project>.supabase.co")
    SUPABASE_ANON_KEY: str = Field(...)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Server-side only. Never expose to client.")
    SUPABASE_JWT_SECRET: str = Field(..., description="Used to verify Supabase-issued JWTs")

    # --- Database (direct Postgres connection, e.g. via Supabase connection pooler) ---
    DATABASE_URL: str = Field(..., description="postgresql+asyncpg://user:pass@host:port/db")

    # --- AI Providers ---
    AI_PROVIDER: str = Field(default="openai")  # openai | gemini
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # --- Scheduler ---
    SCRAPE_INTERVAL_HOURS: int = 6
    RUN_SCHEDULER_IN_PROCESS: bool = Field(
        default=True,
        description="False when the scheduler runs as a separate worker service (multi-instance deploys)",
    )
    MATCH_MIN_SCORE: float = 0.55  # 0-1 similarity threshold to persist a match

    # --- Notifications ---
    NOTIFICATIONS_ENABLED: bool = True

    # --- Rate limiting / scraping etiquette ---
    SCRAPER_REQUEST_TIMEOUT_SECONDS: int = 20
    SCRAPER_MAX_CONCURRENCY: int = 5
    SCRAPER_USER_AGENT: str = "AIJobScavengerBot/1.0 (+https://example.com/bot)"

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use this via FastAPI Depends(get_settings)."""
    return Settings()
