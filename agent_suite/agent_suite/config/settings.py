"""Application settings using environment variables."""

from functools import lru_cache
from typing import List

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base configuration for the Agent Suite application."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = Field(default="", description="OpenAI compatible API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    groq_api_key: str = Field(default="", description="GroqCloud API key")

    postgres_dsn: AnyUrl = Field(
        default="postgresql+asyncpg://agent_suite:agent_suite@localhost:5432/agent_suite",
        description="PostgreSQL DSN for SQLAlchemy async engine",
    )
    vector_store: str = Field(default="pgvector", description="Semantic store backend identifier")

    embeddings_model: str = Field(default="text-embedding-3-large", description="Embedding model name")
    llm_model: str = Field(default="gpt-4-turbo", description="Default LLM model name")
    temperature: float = Field(default=0.2, ge=0, le=1, description="Default sampling temperature")

    job_sources: List[str] = Field(
        default_factory=lambda: ["indeed", "linkedin", "google_jobs"],
        description="External job source identifiers",
    )
    allowed_email_domains: List[str] = Field(
        default_factory=lambda: ["gmail.com", "outlook.com"],
        description="Allowed email domains for sender agent",
    )
    observability_endpoint: str = Field(
        default="http://localhost:9090",
        description="Prometheus push gateway endpoint for metrics",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
