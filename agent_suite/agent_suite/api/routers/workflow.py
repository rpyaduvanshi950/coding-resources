"""Routes for executing the Agent Suite workflow."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agent_suite.workflows import ApplicationState, ApplicationWorkflow

router = APIRouter(prefix="/workflow", tags=["workflow"])


class Project(BaseModel):
    name: str
    description: str
    impact: str = ""


class ProfilePayload(BaseModel):
    full_name: str
    email: str
    education: List[str]
    skills: List[str]
    projects: List[Project] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class WorkflowRequest(BaseModel):
    profile: ProfilePayload
    auto_send: bool = True


class WorkflowResponse(BaseModel):
    dashboard: List[Dict[str, Any]]
    submissions: List[Dict[str, Any]]
    review_status: str


@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest) -> WorkflowResponse:
    workflow = ApplicationWorkflow()
    final_state = await workflow.run(ApplicationState(profile=request.profile.model_dump(), auto_send=request.auto_send))
    if request.auto_send is False and final_state.get("review_status") != "auto":
        raise HTTPException(status_code=202, detail="Awaiting human review")
    return WorkflowResponse(
        dashboard=final_state.get("dashboard", []),
        submissions=final_state.get("submissions", []),
        review_status=final_state.get("review_status", "unknown"),
    )


__all__ = ["router"]
