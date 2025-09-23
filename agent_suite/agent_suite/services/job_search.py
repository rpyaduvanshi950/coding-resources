"""Job search service with pluggable data sources."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from structlog import get_logger

from agent_suite.services.embedding import EmbeddingService

logger = get_logger(__name__)


@dataclass
class SearchFilters:
    """Filtering options provided to the job search service."""

    keywords: List[str]
    locations: Optional[List[str]] = None
    remote: Optional[bool] = None
    min_score: float = 0.0


class JobSearchService:
    """Loads and ranks job postings using semantic similarity."""

    def __init__(self, embedding_service: Optional[EmbeddingService] = None) -> None:
        self._embedding_service = embedding_service or EmbeddingService()
        self._data_path = Path(__file__).resolve().parents[1] / "data" / "sample_jobs.json"

    def _load_jobs(self) -> List[Dict[str, Any]]:
        """Load job postings from configured sources."""

        if not self._data_path.exists():  # pragma: no cover - runtime guard
            logger.warning("Sample job dataset not found", path=str(self._data_path))
            return []
        with self._data_path.open() as handle:
            return json.load(handle)

    def _compute_similarity(self, profile_embedding: List[float], job: Dict[str, Any]) -> float:
        job_vector = self._embedding_service.embed_query(
            " ".join([job["title"], job["company"], job.get("description", "")])
        )
        if not profile_embedding or not job_vector:
            return 0.0
        length = min(len(profile_embedding), len(job_vector))
        score = sum(profile_embedding[i] * job_vector[i] for i in range(length))
        return score / length

    def search(self, profile: Dict[str, Any], filters: SearchFilters) -> List[Dict[str, Any]]:
        """Return ranked job postings for the given profile."""

        profile_vector = self._embedding_service.embed_query(
            " ".join(profile.get("skills", []) + profile.get("interests", []))
        )
        matched_jobs: List[Dict[str, Any]] = []
        for job in self._load_jobs():
            if filters.locations and job.get("location") not in filters.locations:
                continue
            if filters.remote is True and "remote" not in job.get("location", "").lower():
                continue
            if filters.remote is False and "remote" in job.get("location", "").lower():
                continue
            if filters.keywords and not any(
                keyword.lower() in (job.get("description", "") + job.get("title", "")).lower()
                for keyword in filters.keywords
            ):
                continue

            score = self._compute_similarity(profile_vector, job)
            if score < filters.min_score:
                continue
            job_copy = dict(job)
            job_copy["ranking_score"] = score
            job_copy["structured_data"] = {
                "skills": job.get("skills", []),
                "keywords": job.get("skills", []),
                "responsibilities": job.get("description", "").split(","),
            }
            if job.get("posted_at"):
                job_copy["posted_at"] = datetime.fromisoformat(job["posted_at"])
            matched_jobs.append(job_copy)

        matched_jobs.sort(key=lambda job: job.get("ranking_score", 0), reverse=True)
        logger.info("search.results", count=len(matched_jobs))
        return matched_jobs


__all__ = ["JobSearchService", "SearchFilters"]
