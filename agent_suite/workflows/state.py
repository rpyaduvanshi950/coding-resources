"""State definitions for the LangGraph workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ApplicationCommunication:
    job_id: str
    cover_letter: str
    email_body: str
    tone: str


@dataclass
class ApplicationSubmission:
    job_id: str
    status: str
    sent_at: str
    transport: str
    cover_letter: str
    email_body: str
    resume: Dict[str, Any]


@dataclass
class TrackingUpdate:
    job_id: str
    status: str
    next_follow_up: str
    last_contact: str


@dataclass
class CareerState:
    profile_input: Dict[str, Any] = field(default_factory=dict)
    job_filters: Dict[str, Any] = field(default_factory=dict)
    human_feedback: Dict[str, Any] = field(default_factory=dict)
    human_edits: Dict[str, Any] = field(default_factory=dict)

    profile: Dict[str, Any] = field(default_factory=dict)
    jobs: List[Dict[str, Any]] = field(default_factory=list)
    parsed_jobs: List[Dict[str, Any]] = field(default_factory=list)
    resumes: List[Dict[str, Any]] = field(default_factory=list)
    communications: List[Dict[str, Any]] = field(default_factory=list)
    applications: List[Dict[str, Any]] = field(default_factory=list)
    tracking: List[Dict[str, Any]] = field(default_factory=list)
    human_review_complete: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_input": self.profile_input,
            "job_filters": self.job_filters,
            "human_feedback": self.human_feedback,
            "human_edits": self.human_edits,
            "profile": self.profile,
            "jobs": self.jobs,
            "parsed_jobs": self.parsed_jobs,
            "resumes": self.resumes,
            "communications": self.communications,
            "applications": self.applications,
            "tracking": self.tracking,
            "human_review_complete": self.human_review_complete,
        }


__all__ = ["CareerState", "ApplicationCommunication", "ApplicationSubmission", "TrackingUpdate"]
