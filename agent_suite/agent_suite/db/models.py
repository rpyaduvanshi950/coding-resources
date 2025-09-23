"""Database models representing core Agent Suite entities."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ApplicationStatus(str, Enum):
    """Lifecycle status for a submitted application."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Profile(Base):
    """User profile containing normalized data and embeddings."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    education: Mapped[List[str]] = mapped_column(ARRAY(String(255)))
    skills: Mapped[List[str]] = mapped_column(ARRAY(String(255)))
    interests: Mapped[List[str]] = mapped_column(ARRAY(String(255)))
    normalized_profile: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    embedding: Mapped[List[float]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resumes: Mapped[List["ResumeVariant"]] = relationship(back_populates="profile")
    applications: Mapped[List["ApplicationLog"]] = relationship(back_populates="profile")


class JobPosting(Base):
    """Normalized job posting data with structured fields."""

    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    url: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    structured_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ranking_score: Mapped[float] = mapped_column(default=0.0)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resumes: Mapped[List["ResumeVariant"]] = relationship(back_populates="job")
    applications: Mapped[List["ApplicationLog"]] = relationship(back_populates="job")


class ResumeVariant(Base):
    """Resume tailored for a specific job posting."""

    __tablename__ = "resume_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), nullable=False)
    variant_name: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    ats_score: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped[Profile] = relationship(back_populates="resumes")
    job: Mapped[JobPosting] = relationship(back_populates="resumes")


class ApplicationLog(Base):
    """Audit log for application submissions and interactions."""

    __tablename__ = "application_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    recruiter_email: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile: Mapped[Profile] = relationship(back_populates="applications")
    job: Mapped[JobPosting] = relationship(back_populates="applications")


__all__ = [
    "ApplicationLog",
    "ApplicationStatus",
    "JobPosting",
    "Profile",
    "ResumeVariant",
]
