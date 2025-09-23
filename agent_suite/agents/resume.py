"""Resume Agent – tailor ATS-friendly resumes for each job."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from agent_suite.agents.base import AgentResult


@dataclass
class ResumeAgent:
    """Generate resume drafts aligned to parsed job descriptions."""

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        profile = state.get("profile", {})
        parsed_jobs: List[dict[str, Any]] = state.get("parsed_jobs", [])
        resumes = []
        for job in parsed_jobs:
            resume = self._build_resume(profile, job)
            resumes.append(resume)
        return AgentResult(payload={"resumes": resumes})

    def _build_resume(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        highlighted_skills = [skill for skill in job.get("requirements", []) if skill in profile.get("skills", [])]
        missing_skills = [skill for skill in job.get("requirements", []) if skill not in highlighted_skills]
        ats_score = round(100 * len(highlighted_skills) / max(len(job.get("requirements", [])) or 1, 1), 2)
        body = [
            f"Name: {profile.get('name')}",
            f"Email: {profile.get('email', 'N/A')}",
            f"Target Role: {job.get('title')} at {job.get('company')}",
            "",
            "Summary:",
            f"- {profile.get('education', 'Education details not provided.')}",
            f"- Expertise in {', '.join(sorted(profile.get('skills', [])))}.",
            "",
            "Highlighted Experience:",
        ]
        for project in profile.get("projects", []):
            body.append(f"- Delivered {project} with measurable impact.")
        body.extend(
            [
                "",
                "Key Match Highlights:",
                *(f"- Demonstrated proficiency in {skill}." for skill in highlighted_skills),
                *(f"- Plan to upskill rapidly on {skill}." for skill in missing_skills),
            ]
        )
        body.append("")
        body.append("Responsibilities Fit:")
        for responsibility in job.get("responsibilities", [])[:5]:
            body.append(f"- {responsibility}")

        return {
            "job_id": job.get("job_id"),
            "ats_score": ats_score,
            "highlighted_skills": highlighted_skills,
            "missing_skills": missing_skills,
            "body": "\n".join(body),
        }


__all__ = ["ResumeAgent"]
