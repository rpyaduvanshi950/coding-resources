"""JD Parser Agent – structures job descriptions into actionable insights."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from agent_suite.agents.base import AgentResult

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class JDParserAgent:
    """Parse job descriptions and extract ATS-friendly insights."""

    ats_keywords_path: Path = DATA_DIR / "ats_keywords.json"

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        jobs: List[dict[str, Any]] = state.get("jobs", [])
        ats_keywords = self._load_ats_keywords()
        parsed_jobs = []
        for job in jobs:
            parsed = self._parse_job(job, ats_keywords)
            parsed_jobs.append(parsed)
        return AgentResult(payload={"parsed_jobs": parsed_jobs})

    def _load_ats_keywords(self) -> Dict[str, List[str]]:
        with self.ats_keywords_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _parse_job(self, job: Dict[str, Any], ats_keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        description = job.get("description", "")
        required_skills = self._extract_keywords(description, ats_keywords)
        responsibilities = self._extract_responsibilities(description)
        ats_tokens = sorted({*required_skills, *description.lower().split()})
        return {
            "job_id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company"),
            "requirements": required_skills,
            "responsibilities": responsibilities,
            "ats_keywords": ats_tokens,
            "source": job.get("source"),
            "location": job.get("location"),
            "score": job.get("score", 0.0),
        }

    def _extract_keywords(self, description: str, ats_keywords: Dict[str, List[str]]) -> List[str]:
        text = description.lower()
        matched: set[str] = set()
        for category_keywords in ats_keywords.values():
            for keyword in category_keywords:
                if keyword in text:
                    matched.add(keyword)
        return sorted(matched)

    def _extract_responsibilities(self, description: str) -> List[str]:
        bullets = re.split(r"[\.;]\s+", description)
        return [bullet.strip().capitalize() for bullet in bullets if len(bullet.split()) > 3]


__all__ = ["JDParserAgent"]
