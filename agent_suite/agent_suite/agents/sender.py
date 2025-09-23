"""Agent that sends applications and logs submissions."""

from __future__ import annotations

from typing import Any, Dict, List

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import EmailSender


class SenderAgent(BaseAgent[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Handles email dispatch and submission logging."""

    name = "sender-agent"

    def __init__(self, email_sender: EmailSender | None = None) -> None:
        self._email_sender = email_sender or EmailSender()

    async def _arun(self, data: List[Dict[str, Any]], context: AgentContext) -> List[Dict[str, Any]]:
        submissions: List[Dict[str, Any]] = []
        for payload in data:
            job = payload["job"]
            recruiter_email = job.get("recruiter_email", "recruiter@example.com")
            subject = f"Application: {job['title']} at {job['company']}"
            email_body = payload["recruiter_email"]
            result = self._email_sender.send_email(
                sender=context.metadata.get("profile", {}).get("email", "candidate@example.com"),
                recipient=recruiter_email,
                subject=subject,
                body=email_body,
            )
            submission = dict(payload)
            submission["send_result"] = result.__dict__
            submissions.append(submission)
        context.metadata["submissions"] = submissions
        return submissions


__all__ = ["SenderAgent"]
