"""Profile agent responsible for ingesting and normalizing user data."""

from __future__ import annotations

from typing import Any, Dict

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import EmbeddingService


class ProfileAgent(BaseAgent[Dict[str, Any], Dict[str, Any]]):
    """Collects profile information and generates embeddings."""

    name = "profile-agent"

    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self._embedding_service = embedding_service or EmbeddingService()

    async def _arun(self, data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        normalized_profile = self._normalize_profile(data)
        embedding = self._embedding_service.embed_query(
            " ".join(normalized_profile.get("skills", []) + normalized_profile.get("interests", []))
        )
        normalized_profile["embedding"] = embedding
        context.metadata["profile"] = normalized_profile
        return normalized_profile

    def _normalize_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            "full_name": profile.get("full_name", "").strip(),
            "email": profile.get("email", "").lower().strip(),
            "education": [item.strip() for item in profile.get("education", [])],
            "skills": sorted({skill.strip() for skill in profile.get("skills", [])}),
            "projects": profile.get("projects", []),
            "interests": sorted({interest.strip() for interest in profile.get("interests", [])}),
            "preferences": profile.get("preferences", {}),
        }
        return normalized


__all__ = ["ProfileAgent"]
