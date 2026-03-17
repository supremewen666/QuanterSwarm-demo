"""Base specialist."""

from __future__ import annotations

from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult


class BaseSpecialist(BaseAgent):
    name = "base"
    role = "specialist"
    supported_regimes: tuple[str, ...] = ()
    supported_tasks: tuple[str, ...] = ()
    cost_hint = "medium"
    priority = 50

    def supports_regime(self, regime: str) -> bool:
        return not self.supported_regimes or regime in self.supported_regimes

    def supports_task(self, task: str) -> bool:
        return not self.supported_tasks or task in self.supported_tasks

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"specialist": self.name, "payload": payload}

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self.execute(self._context_to_dict(context))
        return self._build_result(payload=payload)
