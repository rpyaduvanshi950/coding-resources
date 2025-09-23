"""Profile Agent – gathers and normalizes candidate information."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_suite.agents.base import AgentResult
from agent_suite.utils.embeddings import hashed_embedding


@dataclass
class ProfileAgent:
    """Collect user details and compute embeddings."""

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        profile_input: dict[str, Any] = state.get("profile_input", {})
        if not profile_input:
            raise ValueError("Profile input is required to start the workflow.")

        normalized_profile = {
            "name": profile_input.get("name"),
            "email": profile_input.get("email"),
            "education": profile_input.get("education"),
            "skills": sorted({skill.lower() for skill in profile_input.get("skills", [])}),
            "projects": profile_input.get("projects", []),
            "preferences": profile_input.get("preferences", {}),
            "embedding": hashed_embedding(
                [profile_input.get("education", "")],
                profile_input.get("skills", []),
                profile_input.get("projects", []),
            ),
        }

        return AgentResult(payload={"profile": normalized_profile})


__all__ = ["ProfileAgent"]
