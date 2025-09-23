"""Communications Agent – crafts cover letters and recruiter emails."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from agent_suite.agents.base import AgentResult


@dataclass
class CommsAgent:
    """Generate personalized communications for each application."""

    def run(self, state: dict[str, Any], **_: Any) -> AgentResult:
        profile = state.get("profile", {})
        parsed_jobs: List[dict[str, Any]] = state.get("parsed_jobs", [])
        resumes: List[dict[str, Any]] = state.get("resumes", [])
        human_feedback: Dict[str, Any] = state.get("human_feedback", {})

        communications = []
        resume_lookup = {resume["job_id"]: resume for resume in resumes}
        for job in parsed_jobs:
            resume = resume_lookup.get(job["job_id"], {})
            communication = self._build_comms(profile, job, resume, human_feedback)
            communications.append(communication)
        return AgentResult(payload={"communications": communications})

    def _build_comms(
        self,
        profile: Dict[str, Any],
        job: Dict[str, Any],
        resume: Dict[str, Any],
        human_feedback: Dict[str, Any],
    ) -> Dict[str, Any]:
        tone = human_feedback.get("cover_letter_tone", "professional")
        highlights = human_feedback.get("email_highlights", [])
        cover_letter = f"""Dear Hiring Manager,\n\nI am excited to apply for the {job['title']} role at {job['company']}. My background in {profile.get('education', 'engineering')} and hands-on experience across {', '.join(profile.get('projects', []))} aligns closely with the position.\n\nKey strengths include {', '.join(resume.get('highlighted_skills', []))}. I am eager to contribute to {job['company']} and learn from the team.\n\nThank you for considering my application.\n\nBest regards,\n{profile.get('name')}\n"""

        if tone == "enthusiastic":
            cover_letter = cover_letter.replace("I am excited", "I am thrilled")

        email_body = f"""Hi {job['company']} Team,\n\nI hope you are well. I just submitted my application for the {job['title']} position. My experience with {', '.join(resume.get('highlighted_skills', [])) or 'relevant AI tooling'} and projects such as {', '.join(profile.get('projects', []))} make me a strong fit. {('Highlights: ' + ', '.join(highlights) + '.') if highlights else ''}\n\nPlease let me know if there is any additional information I can share.\n\nRegards,\n{profile.get('name')}\n{profile.get('email', '')}"""

        return {
            "job_id": job.get("job_id"),
            "cover_letter": cover_letter,
            "email_body": email_body,
            "tone": tone,
        }


__all__ = ["CommsAgent"]
