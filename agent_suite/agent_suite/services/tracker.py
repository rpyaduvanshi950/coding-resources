"""Application tracking service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict, List

from structlog import get_logger

logger = get_logger(__name__)


@dataclass
class ApplicationEvent:
    """Represents a tracked event for an application."""

    timestamp: datetime
    status: str
    notes: str = ""


@dataclass
class TrackedApplication:
    """State container for an individual application."""

    job_title: str
    company: str
    status: str
    events: List[ApplicationEvent] = field(default_factory=list)


class ApplicationTracker:
    """Stores and updates application statuses."""

    def __init__(self) -> None:
        self._applications: Dict[str, TrackedApplication] = {}

    def log_event(self, job_id: str, job_title: str, company: str, status: str, notes: str = "") -> TrackedApplication:
        key = f"{job_id}:{company}"
        event = ApplicationEvent(timestamp=datetime.now(UTC), status=status, notes=notes)
        application = self._applications.get(key)
        if application is None:
            application = TrackedApplication(job_title=job_title, company=company, status=status)
            self._applications[key] = application
        application.events.append(event)
        application.status = status
        logger.info("tracker.log", job_id=job_id, status=status)
        return application

    def dashboard(self) -> List[TrackedApplication]:
        return list(self._applications.values())


__all__ = ["ApplicationTracker", "TrackedApplication", "ApplicationEvent"]
