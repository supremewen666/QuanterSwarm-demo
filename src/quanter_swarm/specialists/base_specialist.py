"""Base specialist."""

from __future__ import annotations

from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult
from quanter_swarm.tools.builtin import build_default_tool_registry
from quanter_swarm.tools.executor import ToolExecutor


class BaseSpecialist(BaseAgent):
    name = "base"
    role = "specialist"
    supported_regimes: tuple[str, ...] = ()
    supported_tasks: tuple[str, ...] = ()
    cost_hint = "medium"
    priority = 50

    def __init__(self, tool_executor: ToolExecutor | None = None) -> None:
        self.tool_executor = tool_executor or ToolExecutor(build_default_tool_registry())

    def supports_regime(self, regime: str) -> bool:
        return not self.supported_regimes or regime in self.supported_regimes

    def supports_task(self, task: str) -> bool:
        return not self.supported_tasks or task in self.supported_tasks

    def _run_tool(self, tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self.tool_executor.execute(tool_name, payload)
        tool_payload = dict(result.get("payload", {}))
        tool_payload.setdefault("status", result.get("status", "ok"))
        tool_payload.setdefault("reason", result.get("reason", ""))
        tool_payload.setdefault("fallback_flags", result.get("fallback_flags", []))
        tool_payload.setdefault("confidence", result.get("confidence", 1.0))
        return tool_payload

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"specialist": self.name, "payload": payload}

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self.execute(self._context_to_dict(context))
        return self._build_result(payload=payload)
