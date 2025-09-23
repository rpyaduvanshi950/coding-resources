"""Sender Agent – dispatch applications via email or APIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from agent_suite.agents.base import AgentResult


@dataclass
class SenderAgent:
    """Simulate sending applications and producing logs."""

    transport: str = "smtp"

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        communications: List[dict[str, Any]] = state.get("communications", [])
        resumes: Dict[str, dict[str, Any]] = {resume["job_id"]: resume for resume in state.get("resumes", [])}
        submissions = []
        for communication in communications:
            job_id = communication["job_id"]
            resume = resumes.get(job_id, {})
            submissions.append(
                {
                    "job_id": job_id,
                    "status": "submitted",
                    "sent_at": datetime.utcnow().isoformat(),
                    "transport": self.transport,
                    "cover_letter": communication.get("cover_letter"),
                    "email_body": communication.get("email_body"),
                    "resume": resume,
                }
            )
        return AgentResult(payload={"applications": submissions})


__all__ = ["SenderAgent"]
