# Agent Suite – AI-Powered Career Assistant

Agent Suite automates and streamlines the end-to-end internship and job application workflow using a team of specialized AI agents orchestrated through LangGraph. The system handles everything from collecting the candidate profile to tracking recruiter responses while keeping a human reviewer in the loop.

## Features

- **Multi-Agent Orchestration:** LangGraph workflow connects Profile, Search, JD Parsing, Resume, Communications, Sending, and Tracking agents with a human review stage.
- **ATS Optimization:** Tailors resumes and cover letters using ATS keyword intelligence and skill gap analysis.
- **Pluggable Data Sources:** Supports internal datasets, scraped job boards, and custom APIs via a unified search abstraction.
- **Production-Ready Backend:** FastAPI service for running pipelines, querying jobs, and managing application states.
- **Observability Hooks:** Structured logging and placeholders for Prometheus, Grafana, and Sentry integration.

## Architecture Overview

```text
┌───────────────────────────────────────────────────────────────────────┐
│                                FastAPI                                 │
│      /pipeline/run, /jobs/search, /applications/{id}/status            │
└───────────────────────────────────────────────────────────────────────┘
                │
                ▼
       LangGraph Career Workflow (StateGraph)
                │
                ▼
┌──────────┬────────┬──────────┬──────────┬──────────┬────────┬──────────┐
│ Profile  │ Search │ JD Parse │ Resume   │ Comms    │ Sender │ Tracker  │
│ Agent    │ Agent  │ Agent    │ Agent    │ Agent    │ Agent  │ Agent    │
└──────────┴────────┴──────────┴──────────┴──────────┴────────┴──────────┘
                ▲
                │
         Human-in-the-loop Review
```

The workflow is defined in [`agent_suite/workflows/career_pipeline.py`](workflows/career_pipeline.py) and can be executed programmatically or through the FastAPI endpoints.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Create a `.env` file (optional) to configure database and integration credentials:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agent_suite
OPENAI_API_KEY=sk-...
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=example@gmail.com
SMTP_PASSWORD=app-specific-password
```

## Database Setup

Agent Suite uses PostgreSQL with `pgvector` for semantic search. Run the SQL migration located at [`database/schema.sql`](../database/schema.sql) to create the schema.

```bash
psql $DATABASE_URL -f database/schema.sql
```

## Usage

### Run the FastAPI Server

```bash
uvicorn agent_suite.api.server:app --reload
```

### Execute the Workflow from Python

```python
from agent_suite.workflows.career_pipeline import build_career_workflow
from agent_suite.workflows.state import CareerState

workflow = build_career_workflow()
initial_state = CareerState(profile_input={
    "name": "Aditi Sharma",
    "education": "B.Tech, IIT Kanpur",
    "skills": ["Python", "LangChain", "FastAPI", "Transformers"],
    "projects": ["Conversational AI Assistant", "Resume Analyzer"],
    "preferences": {"location": "Remote", "role": "AI"}
})

result = workflow.invoke(initial_state)
print(result.applications[0].cover_letter)
```

### Example API Workflow

1. `POST /pipeline/run` with the payload from [`examples/pipeline_request.json`](../examples/pipeline_request.json).
2. Review the generated artifacts and optionally update the draft documents.
3. Confirm sending via `POST /applications/{application_id}/send`.

## Observability

Structured logs are emitted using Python's standard logging module. Integrations for Prometheus metrics and Sentry tracing are stubbed and can be connected using the hooks in `agent_suite/utils/telemetry.py`.

## Tests

Run unit tests to validate the orchestration logic.

```bash
pytest
```

## Roadmap

- Live ATS scoring integrations (e.g., Greenhouse, Lever)
- Expanded job source adapters and crawling
- Calendar integrations for follow-up scheduling
- Analytics dashboard built with React + FastAPI

## License

MIT
