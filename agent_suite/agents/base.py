"""Base classes and typing helpers for agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AgentResult:
    """Container for agent outputs."""

    payload: dict[str, Any]
    metrics: dict[str, Any] | None = None


class Agent(Protocol):
    """Protocol implemented by all agents."""

    def run(self, state: dict[str, Any], **kwargs: Any) -> AgentResult:
        """Execute the agent and return structured results."""


__all__ = ["AgentResult", "Agent"]
