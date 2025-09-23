"""Example script running the Agent Suite workflow end-to-end."""

from __future__ import annotations

import asyncio
from pprint import pprint

from agent_suite.workflows import ApplicationState, ApplicationWorkflow


async def main() -> None:
    workflow = ApplicationWorkflow()
    example_profile = {
        "full_name": "Aditi Sharma",
        "email": "aditi@example.com",
        "education": ["B.Tech Computer Science – IIT Kanpur"],
        "skills": ["Python", "Machine Learning", "LangChain", "FastAPI"],
        "projects": [
            {
                "name": "Autonomous Agent Research",
                "description": "Explored multi-agent coordination for job search automation.",
                "impact": "Improved matching accuracy by 25%",
            }
        ],
        "interests": ["AI Research", "Autonomous Agents"],
        "preferences": {"keywords": ["AI", "research"], "locations": ["Kanpur, India", "Remote"], "remote": True},
    }
    result = await workflow.run(ApplicationState(profile=example_profile, auto_send=True))
    pprint(result)


if __name__ == "__main__":
    asyncio.run(main())
