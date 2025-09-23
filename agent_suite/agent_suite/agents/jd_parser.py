"""Agent that converts raw job descriptions into structured insights."""

from __future__ import annotations

from typing import Any, Dict, List

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import JobDescriptionParser


class JobDescriptionParserAgent(BaseAgent[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Parses job descriptions to augment job postings."""

    name = "jd-parser-agent"

    def __init__(self, parser: JobDescriptionParser | None = None) -> None:
        self._parser = parser or JobDescriptionParser()

    async def _arun(self, data: List[Dict[str, Any]], context: AgentContext) -> List[Dict[str, Any]]:
        parsed_jobs: List[Dict[str, Any]] = []
        for job in data:
            structured = self._parser.parse(job.get("description", ""))
            enriched_job = dict(job)
            enriched_job.setdefault("structured_data", {}).update(structured)
            parsed_jobs.append(enriched_job)
        context.metadata["parsed_jobs"] = parsed_jobs
        return parsed_jobs


__all__ = ["JobDescriptionParserAgent"]
