from agent_suite.workflows.career_pipeline import run_pipeline
from agent_suite.workflows.state import CareerState


def test_pipeline_generates_artifacts():
    state = CareerState(
        profile_input={
            "name": "Test User",
            "email": "test@example.com",
            "education": "B.Tech, IIT Kanpur",
            "skills": ["python", "langchain", "fastapi", "sql"],
            "projects": ["AI Mentor", "Career Tracker"],
            "preferences": {"location": "Remote"},
        },
        job_filters={"keywords": ["AI", "Data"], "locations": ["Remote", "Kanpur"]},
        human_feedback={"cover_letter_tone": "professional"},
    )

    result = run_pipeline(state)
    assert result.profile["name"] == "Test User"
    assert result.jobs, "Expected at least one job"
    assert len(result.resumes) == len(result.parsed_jobs)
    assert all("cover_letter" in item for item in result.communications)
    assert all(item["status"] == "submitted" for item in result.applications)
    assert all("next_follow_up" in item for item in result.tracking)
