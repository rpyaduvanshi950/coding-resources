"""Search Agent – discovers relevant job opportunities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List

from agent_suite.agents.base import AgentResult
from agent_suite.utils.embeddings import hashed_embedding


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class SearchFilters:
    keywords: Iterable[str] | None = None
    locations: Iterable[str] | None = None
    sources: Iterable[str] | None = None


@dataclass
class SearchAgent:
    """Search local datasets and remote APIs to surface jobs."""

    dataset_path: Path = DATA_DIR / "sample_jobs.json"

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        profile = state.get("profile", {})
        filters_data = state.get("job_filters", {})
        filters = SearchFilters(
            keywords=filters_data.get("keywords"),
            locations=filters_data.get("locations"),
            sources=filters_data.get("sources"),
        )

        jobs = self._load_jobs()
        scored_jobs = self._score_jobs(jobs, profile, filters)
        ranked = sorted(scored_jobs, key=lambda job: job["score"], reverse=True)

        return AgentResult(payload={"jobs": ranked})

    def _load_jobs(self) -> List[dict[str, Any]]:
        with self.dataset_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _score_jobs(
        self,
        jobs: Iterable[dict[str, Any]],
        profile: dict[str, Any],
        filters: SearchFilters,
    ) -> List[dict[str, Any]]:
        results: List[dict[str, Any]] = []
        profile_skills = set(profile.get("skills", []))
        for job in jobs:
            if filters.keywords and not any(
                keyword.lower() in job["description"].lower() or keyword.lower() in job["title"].lower()
                for keyword in filters.keywords
            ):
                continue
            if filters.locations and job.get("location") not in filters.locations:
                continue
            if filters.sources and job.get("source") not in filters.sources:
                continue

            job_skills = set(token for token in job.get("description", "").lower().replace(",", "").split())
            overlap = len(profile_skills & job_skills)
            embedding = hashed_embedding([job.get("title", "")], [job.get("description", "")])
            results.append({
                **job,
                "score": overlap + 0.1 * len(job.get("description", "")),
                "embedding": embedding,
            })
        return results


__all__ = ["SearchAgent"]
