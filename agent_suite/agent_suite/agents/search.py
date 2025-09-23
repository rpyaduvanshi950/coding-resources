"""Agent for searching and ranking job opportunities."""

from __future__ import annotations

from typing import Any, Dict, List

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import JobSearchService, SearchFilters


class SearchAgent(BaseAgent[Dict[str, Any], List[Dict[str, Any]]]):
    """Queries job sources and returns ranked opportunities."""

    name = "search-agent"

    def __init__(self, job_search_service: JobSearchService | None = None) -> None:
        self._job_search_service = job_search_service or JobSearchService()

    async def _arun(self, data: Dict[str, Any], context: AgentContext) -> List[Dict[str, Any]]:
        profile = context.metadata.get("profile") or data.get("profile")
        preferences = profile.get("preferences", {}) if profile else {}
        filters = SearchFilters(
            keywords=preferences.get("keywords", []),
            locations=preferences.get("locations"),
            remote=preferences.get("remote"),
            min_score=preferences.get("min_score", 0.0),
        )
        jobs = self._job_search_service.search(profile, filters)
        context.metadata["jobs"] = jobs
        return jobs


__all__ = ["SearchAgent"]
