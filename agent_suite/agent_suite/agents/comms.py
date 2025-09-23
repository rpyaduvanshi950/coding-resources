"""Agent that generates cover letters and recruiter emails."""

from __future__ import annotations

from typing import Any, Dict, List

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import CommunicationsBuilder


class CommunicationsAgent(BaseAgent[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Produces personalized communications for each job."""

    name = "communications-agent"

    def __init__(self, builder: CommunicationsBuilder | None = None) -> None:
        self._builder = builder or CommunicationsBuilder()

    async def _arun(self, data: List[Dict[str, Any]], context: AgentContext) -> List[Dict[str, Any]]:
        profile = context.metadata.get("profile", {})
        comms_payloads: List[Dict[str, Any]] = []
        for resume in data:
            job = resume["job"]
            communications = self._builder.build(profile, job)
            payload = dict(resume)
            payload.update(
                {
                    "cover_letter": communications.cover_letter,
                    "recruiter_email": communications.recruiter_email,
                }
            )
            comms_payloads.append(payload)
        context.metadata["communications"] = comms_payloads
        return comms_payloads


__all__ = ["CommunicationsAgent"]
