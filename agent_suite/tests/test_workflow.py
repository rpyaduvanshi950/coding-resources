"""Unit tests for the application workflow."""

from __future__ import annotations

import pytest

from agent_suite.workflows import ApplicationState, ApplicationWorkflow


@pytest.mark.asyncio
async def test_workflow_auto_send() -> None:
    workflow = ApplicationWorkflow()
    profile = {
        "full_name": "Test Candidate",
        "email": "test@example.com",
        "education": ["B.Tech"],
        "skills": ["Python", "FastAPI"],
        "projects": [
            {"name": "Project A", "description": "Desc", "impact": "Impact"},
        ],
        "interests": ["AI"],
        "preferences": {"keywords": ["AI"], "remote": True},
    }
    result = await workflow.run(ApplicationState(profile=profile, auto_send=True))
    assert result["review_status"] == "auto"
    assert result["submissions"], "Expected submissions to be generated"
    assert result["dashboard"], "Expected dashboard entries"


@pytest.mark.asyncio
async def test_workflow_requires_review() -> None:
    workflow = ApplicationWorkflow()
    profile = {
        "full_name": "Review Candidate",
        "email": "review@example.com",
        "education": ["M.Tech"],
        "skills": ["Research", "Python"],
        "projects": [],
        "interests": ["Research"],
        "preferences": {"keywords": ["Research"], "remote": True},
    }
    result = await workflow.run(ApplicationState(profile=profile, auto_send=False))
    assert result["review_status"] == "pending"
    assert "submissions" not in result or not result["submissions"]
