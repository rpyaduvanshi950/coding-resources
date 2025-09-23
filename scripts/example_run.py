"""Example execution of the Agent Suite pipeline."""

from __future__ import annotations

from pprint import pprint

from agent_suite.workflows.career_pipeline import run_pipeline
from agent_suite.workflows.state import CareerState


if __name__ == "__main__":
    state = CareerState(
        profile_input={
            "name": "Aditi Sharma",
            "email": "aditi@example.com",
            "education": "B.Tech, IIT Kanpur",
            "skills": ["python", "langchain", "fastapi", "transformers"],
            "projects": ["Conversational AI Assistant", "Resume Analyzer"],
            "preferences": {"location": "Remote", "role": "AI"},
        },
        job_filters={"keywords": ["AI"], "locations": ["Remote", "Kanpur"]},
        human_feedback={"cover_letter_tone": "enthusiastic"},
    )

    result = run_pipeline(state)
    pprint(result.to_dict())
