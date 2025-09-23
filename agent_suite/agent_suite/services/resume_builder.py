"""Resume tailoring utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from jinja2 import Environment, PackageLoader, select_autoescape


@dataclass
class ResumeBuildResult:
    """Structured result for a resume variant."""

    name: str
    content: str
    ats_score: float


class ResumeBuilder:
    """Generate ATS friendly resumes by matching profile and job requirements."""

    def __init__(self) -> None:
        self._jinja_env = Environment(
            loader=PackageLoader("agent_suite", "templates"),
            autoescape=select_autoescape(),
        )

    def build(self, profile: Dict[str, Any], job: Dict[str, Any]) -> ResumeBuildResult:
        template = self._jinja_env.get_template("resume_template.j2")
        matched_skills = self._match_skills(
            profile.get("skills", []), job.get("structured_data", {}).get("keywords", [])
        )
        ats_score = self._compute_ats_score(profile, job)
        content = template.render(
            profile=profile,
            job=job,
            matched_skills=matched_skills,
            ats_score=ats_score,
        )
        variant_name = f"{job['title']} - {job['company']}"
        return ResumeBuildResult(name=variant_name, content=content, ats_score=ats_score)

    def _match_skills(self, profile_skills: List[str], job_keywords: List[str]) -> List[str]:
        lower_keywords = {keyword.lower() for keyword in job_keywords}
        return [skill for skill in profile_skills if skill.lower() in lower_keywords]

    def _compute_ats_score(self, profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        job_keywords = job.get("structured_data", {}).get("keywords", [])
        if not job_keywords:
            return 0.0
        matched = len(self._match_skills(profile.get("skills", []), job_keywords))
        score = matched / len(job_keywords)
        return round(score, 2)


__all__ = ["ResumeBuilder", "ResumeBuildResult"]
