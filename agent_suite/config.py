"""Configuration helpers for Agent Suite."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or .env files."""

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agent_suite",
        description="SQLAlchemy connection string for PostgreSQL with pgvector.",
    )
    openai_api_key: Optional[str] = Field(default=None, description="Optional OpenAI API key.")
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    telemetry_enabled: bool = Field(default=False)

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()  # type: ignore[arg-type]


__all__ = ["Settings", "get_settings"]
