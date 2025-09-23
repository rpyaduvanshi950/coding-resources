# Agent Suite – AI-Powered Career Assistant

Agent Suite automates the end-to-end job and internship application pipeline using a LangGraph-powered multi-agent workflow. The project demonstrates how specialized AI agents can collaborate to research opportunities, tailor materials, communicate with recruiters, and track outcomes.

## Key Features

- **Profile Agent** – normalizes candidate data and generates embeddings for semantic search.
- **Search Agent** – queries job sources (sample dataset, pluggable architecture) and ranks results using embedding similarity.
- **JD Parser Agent** – converts job descriptions into structured JSON (skills, keywords, responsibilities).
- **Resume Agent** – creates ATS-friendly resume variants per role via templating and scoring heuristics.
- **Communications Agent** – drafts cover letters and recruiter emails with tone customization.
- **Human-in-the-loop Node** – optional pause for manual edits before submission.
- **Sender Agent** – dispatches emails (Gmail/SMTP ready interface) and logs submissions.
- **Tracker Agent** – maintains an application dashboard with follow-up events.

The workflow is orchestrated through LangGraph, enabling modular nodes, conditional routing, and asynchronous execution.

## Architecture Overview

```
Profile Agent -> Search Agent -> JD Parser -> Resume Agent -> Comms Agent
        -> Human Review -> Sender Agent -> Tracker Agent
```

Supporting services provide embeddings, job search abstractions, resume and communications templating, email sending, and tracking. The backend is exposed via FastAPI for integration with UIs or automation scripts.

## Tech Stack

- **Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) for graph-based agent orchestration.
- **Backend**: FastAPI with modular routers.
- **Data & Storage**: SQLAlchemy models for PostgreSQL/pgvector, FAISS-ready embeddings, JSON sample datasets.
- **File Generation**: Jinja2 templates (extendable to `python-docx` or `reportlab`).
- **Email Integration**: Gmail/SMTP-ready abstraction with logging.
- **Scraping**: Playwright + BeautifulSoup/selectolax placeholders (extend job search service).
- **Observability Hooks**: Structlog logging, Prometheus/Sentry ready.

## Project Layout

```
agent_suite/
├── agent_suite/
│   ├── agents/               # Agent implementations
│   ├── api/                  # FastAPI app and routers
│   ├── config/               # Typed settings management
│   ├── data/                 # Sample datasets (jobs, templates)
│   ├── db/                   # SQLAlchemy models and engine
│   ├── services/             # Shared services (search, resume, comms, etc.)
│   ├── templates/            # Jinja2 templates for resumes & emails
│   └── workflows/            # LangGraph workflow definitions
├── scripts/
│   └── run_example.py        # Run the workflow end-to-end
├── tests/
│   └── test_workflow.py      # Pytest coverage for workflow paths
└── pyproject.toml            # Dependencies and tooling
```

## Installation

1. Ensure Python 3.11+ is installed.
2. Install dependencies (Poetry recommended):

```bash
cd agent_suite
poetry install
# or: pip install -e .
```

3. Export any required API keys (e.g., `OPENAI_API_KEY`) if using hosted LLMs.

## Running the Workflow

### Command Line Example

```
poetry run python scripts/run_example.py
```

The script prints the final workflow state including submissions and dashboard events.

### FastAPI Server

```
poetry run uvicorn agent_suite.api.main:app --reload
```

Invoke the `/workflow/run` endpoint with a JSON payload:

```json
{
  "profile": {
    "full_name": "Aditi Sharma",
    "email": "aditi@example.com",
    "education": ["B.Tech Computer Science – IIT Kanpur"],
    "skills": ["Python", "Machine Learning", "LangChain", "FastAPI"],
    "projects": [
      {"name": "Autonomous Agent Research", "description": "...", "impact": "Improved matching accuracy by 25%"}
    ],
    "interests": ["AI Research", "Autonomous Agents"],
    "preferences": {"keywords": ["AI", "research"], "locations": ["Kanpur, India", "Remote"], "remote": true}
  },
  "auto_send": true
}
```

If `auto_send` is `false`, the workflow halts at the human review node and returns HTTP 202 to signal manual intervention before resuming.

## Extending the System

- **Job Sources**: Replace `services/job_search.py` with live scrapers (Playwright + BeautifulSoup/selectolax) and integrate API keys for LinkedIn/Indeed.
- **Resume Generation**: Swap templating with `python-docx` or `reportlab` exporters, attach PDFs to emails.
- **Communication Personalization**: Integrate LLM prompts via LangChain to generate richer emails and follow-up schedules.
- **Sender Agent**: Connect Gmail API/OAuth credentials for real deliveries.
- **Tracker**: Persist to PostgreSQL and visualize metrics via Grafana; feed Prometheus counters and Sentry breadcrumbs.
- **Evaluation**: Compare ATS scores from baseline vs tailored resumes and conduct live testing on IIT Kanpur research openings.

## Testing

Run the automated tests with:

```
poetry run pytest
```

## License

MIT License. See `pyproject.toml` for attribution details.
