"""Base agent definitions used across the workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

from langchain_core.runnables import RunnableConfig


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass
class AgentContext:
    """Shared context passed between agents in the workflow."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Optional[RunnableConfig] = None


@dataclass
class AgentResult(Generic[OutputT]):
    """Standardized result returned by all agents."""

    output: OutputT
    context: AgentContext


class BaseAgent(Generic[InputT, OutputT]):
    """Base class providing lifecycle hooks for agents."""

    name: str = "base-agent"

    async def arun(self, data: InputT, context: AgentContext) -> AgentResult[OutputT]:
        """Asynchronous entrypoint for agent execution."""

        output = await self._arun(data, context)
        return AgentResult(output=output, context=context)

    async def _arun(self, data: InputT, context: AgentContext) -> OutputT:  # pragma: no cover - to override
        raise NotImplementedError


__all__ = ["AgentContext", "AgentResult", "BaseAgent"]
