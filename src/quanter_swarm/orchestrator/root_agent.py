"""Root orchestration entry point."""

from __future__ import annotations

import asyncio
from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult, CycleReport
from quanter_swarm.orchestrator.cycle_manager import CycleManager


class RootAgent(BaseAgent):
    name = "root"
    role = "orchestrator"

    def run_sync(self, symbol: str | None = None, scenario: dict[str, Any] | None = None) -> dict[str, Any]:
        result = CycleManager().run_cycle(symbol=symbol, scenario=scenario)
        return CycleReport.model_validate(result).model_dump()

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self._context_to_dict(context)
        report = await asyncio.to_thread(
            self.run_sync,
            payload.get("symbol"),
            payload.get("scenario"),
        )
        return self._build_result(summary=str(report["active_regime"]), payload=report)
