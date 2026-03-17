"""Routing decisions."""

from __future__ import annotations

from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult
from quanter_swarm.router import select_leader


class RouterAgent(BaseAgent):
    name = "router"
    role = "orchestrator"

    def route(self, regime: str | dict[str, Any], router_config: dict[str, Any], regimes_config: dict[str, Any]) -> dict[str, Any]:
        return select_leader(regime, router_config, regimes_config)

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self._context_to_dict(context)
        result = self.route(
            payload["regime"],
            payload.get("router_config", {}),
            payload.get("regimes_config", {}),
        )
        return self._build_result(summary=str(result["regime"]), payload=result)
