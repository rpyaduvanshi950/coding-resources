"""Tracker Agent – monitor recruiter responses and follow-ups."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

from agent_suite.agents.base import AgentResult


@dataclass
class TrackerAgent:
    """Update application statuses and schedule follow-ups."""

    follow_up_days: int = 5

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        applications: List[dict[str, Any]] = state.get("applications", [])
        updates = []
        for application in applications:
            follow_up_date = (datetime.fromisoformat(application["sent_at"]) + timedelta(days=self.follow_up_days)).date()
            updates.append(
                {
                    "job_id": application["job_id"],
                    "status": application.get("status", "submitted"),
                    "next_follow_up": follow_up_date.isoformat(),
                    "last_contact": application["sent_at"],
                }
            )
        return AgentResult(payload={"tracking": updates})


__all__ = ["TrackerAgent"]
