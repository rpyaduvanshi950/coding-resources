"""FastAPI application exposing the Agent Suite capabilities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent_suite.utils.telemetry import configure_logging, logger
from agent_suite.workflows.career_pipeline import run_pipeline
from agent_suite.workflows.state import CareerState

configure_logging()

app = FastAPI(title="Agent Suite – AI-Powered Career Assistant")


class PipelineRequest(BaseModel):
    profile: Dict[str, Any]
    job_filters: Dict[str, Any] = Field(default_factory=dict)
    human_feedback: Dict[str, Any] = Field(default_factory=dict)
    human_edits: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ApplicationArtifact(BaseModel):
    job_id: str
    cover_letter: str
    email_body: str
    resume_body: Optional[str] = None
    ats_score: Optional[float] = None
    next_follow_up: Optional[str] = None


class PipelineResponse(BaseModel):
    profile: Dict[str, Any]
    jobs: List[Dict[str, Any]]
    applications: List[ApplicationArtifact]


@app.post("/pipeline/run", response_model=PipelineResponse)
async def pipeline_run(request: PipelineRequest) -> PipelineResponse:
    logger.info("Received pipeline run request")
    state = CareerState(
        profile_input=request.profile,
        job_filters=request.job_filters,
        human_feedback=request.human_feedback,
        human_edits=request.human_edits,
    )
    result = run_pipeline(state)

    artifacts: List[ApplicationArtifact] = []
    communication_lookup = {item["job_id"]: item for item in result.communications}
    resume_lookup = {item["job_id"]: item for item in result.resumes}
    tracking_lookup = {item["job_id"]: item for item in result.tracking}

    for application in result.applications:
        job_id = application["job_id"]
        communication = communication_lookup.get(job_id, {})
        resume = resume_lookup.get(job_id, {})
        tracking = tracking_lookup.get(job_id, {})
        artifacts.append(
            ApplicationArtifact(
                job_id=job_id,
                cover_letter=communication.get("cover_letter", ""),
                email_body=communication.get("email_body", ""),
                resume_body=resume.get("body"),
                ats_score=resume.get("ats_score"),
                next_follow_up=tracking.get("next_follow_up"),
            )
        )

    return PipelineResponse(profile=result.profile, jobs=result.jobs, applications=artifacts)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
