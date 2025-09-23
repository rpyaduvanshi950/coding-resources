"""Database models for Agent Suite."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, TIMESTAMP, BigInteger, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID, VECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base class."""

    type_annotation_map = {list[str]: ARRAY(String())}


class UserProfile(Base):
    """Candidate profile captured by the Profile Agent."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    projects: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    preferences: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(VECTOR(768), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    applications: Mapped[list["Application"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class JobPosting(Base):
    """Job postings discovered by the Search Agent."""

    __tablename__ = "job_postings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(VECTOR(768), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    applications: Mapped[list["Application"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    """Application drafts and submissions."""

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    job_id: Mapped[str] = mapped_column(String, ForeignKey("job_postings.id"))
    resume_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cover_letter_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="draft")
    ats_score: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    user: Mapped[UserProfile] = relationship(back_populates="applications")
    job: Mapped[JobPosting] = relationship(back_populates="applications")
    logs: Mapped[list["ApplicationLog"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class ApplicationLog(Base):
    """Event log for applications."""

    __tablename__ = "application_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"))
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    application: Mapped[Application] = relationship(back_populates="logs")


__all__ = [
    "Base",
    "UserProfile",
    "JobPosting",
    "Application",
    "ApplicationLog",
]
