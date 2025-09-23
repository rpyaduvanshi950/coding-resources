"""SQLAlchemy async engine and session configuration."""

from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from agent_suite.config import get_settings


settings = get_settings()


class Base(AsyncAttrs, DeclarativeBase):
    """Declarative base class that supports async flush/refresh."""


async_engine = create_async_engine(str(settings.postgres_dsn), echo=False)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

__all__ = ["Base", "async_engine", "async_session_factory"]
