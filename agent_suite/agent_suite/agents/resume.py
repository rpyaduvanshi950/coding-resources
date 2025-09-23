"""Agent that tailors resumes for each job posting."""

from __future__ import annotations

from typing import Any, Dict, List

from agent_suite.agents.base import AgentContext, BaseAgent
from agent_suite.services import ResumeBuilder


class ResumeAgent(BaseAgent[List[Dict[str, Any]], List[Dict[str, Any]]]):
    """Generates ATS optimized resume variants."""

    name = "resume-agent"

    def __init__(self, resume_builder: ResumeBuilder | None = None) -> None:
        self._resume_builder = resume_builder or ResumeBuilder()

    async def _arun(self, data: List[Dict[str, Any]], context: AgentContext) -> List[Dict[str, Any]]:
        profile = context.metadata.get("profile", {})
        resume_variants: List[Dict[str, Any]] = []
        for job in data:
            resume_result = self._resume_builder.build(profile, job)
            resume_variants.append(
                {
                    "job": job,
                    "variant_name": resume_result.name,
                    "content": resume_result.content,
                    "ats_score": resume_result.ats_score,
                }
            )
        context.metadata["resumes"] = resume_variants
        return resume_variants


__all__ = ["ResumeAgent"]
