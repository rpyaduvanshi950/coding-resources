"""FastAPI entrypoint for Agent Suite."""

from __future__ import annotations

from fastapi import FastAPI

from agent_suite.api.routers import workflow_router


def create_app() -> FastAPI:
    app = FastAPI(title="Agent Suite – AI-Powered Career Assistant", version="0.1.0")

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(workflow_router)
    return app


app = create_app()

__all__ = ["create_app", "app"]
