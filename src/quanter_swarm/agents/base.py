"""Shared base interface for all agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from quanter_swarm.contracts import AgentContext, AgentResult


class BaseAgent(ABC):
    name: str = "base"
    role: str = "agent"

    def _context_to_dict(self, context: AgentContext | dict[str, Any]) -> dict[str, Any]:
        if isinstance(context, AgentContext):
            return context.model_dump(exclude_none=True)
        return dict(context)

    def _build_result(self, *, summary: str = "", payload: dict[str, Any] | None = None) -> AgentResult:
        return AgentResult(agent_name=self.name, role=self.role, summary=summary, payload=payload or {})

    @abstractmethod
    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        """Execute the agent against the provided context."""
