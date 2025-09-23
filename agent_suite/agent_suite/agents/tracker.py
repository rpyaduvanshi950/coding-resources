"""Agent that updates the application tracker dashboard."""

from __future__ import annotations

from typing import Any, Dict, List

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import ApplicationTracker


class TrackerAgent(BaseAgent[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Tracks responses and follow-up actions."""

    name = "tracker-agent"

    def __init__(self, tracker: ApplicationTracker | None = None) -> None:
        self._tracker = tracker or ApplicationTracker()

    async def _arun(self, data: List[Dict[str, Any]], context: AgentContext) -> List[Dict[str, Any]]:
        dashboard_entries: List[Dict[str, Any]] = []
        for submission in data:
            job = submission["job"]
            result = self._tracker.log_event(
                job_id=str(job.get("id", job.get("url", "unknown"))),
                job_title=job.get("title", "Unknown"),
                company=job.get("company", "Unknown"),
                status="submitted" if submission.get("send_result", {}).get("success") else "error",
                notes=submission.get("send_result", {}).get("error", ""),
            )
            dashboard_entries.append(
                {
                    "job": job,
                    "status": result.status,
                    "events": [event.__dict__ for event in result.events],
                }
            )
        context.metadata["dashboard"] = dashboard_entries
        return dashboard_entries


__all__ = ["TrackerAgent"]
