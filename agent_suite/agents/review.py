"""Human-in-the-loop review node."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_suite.agents.base import AgentResult


@dataclass
class ReviewAgent:
    """Simulate a human review stage by applying manual edits."""

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        edits = state.get("human_edits", {})
        communications = state.get("communications", [])
        if edits:
            for communication in communications:
                job_id = communication.get("job_id")
                if job_id in edits:
                    job_edits = edits[job_id]
                    communication.update(job_edits)
        return AgentResult(payload={"communications": communications, "human_review_complete": True})


__all__ = ["ReviewAgent"]
