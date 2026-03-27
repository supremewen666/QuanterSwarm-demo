"""Root orchestration entry point."""

from __future__ import annotations

import asyncio
from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.agents.orchestrator.cycle_manager import CycleManager
from quanter_swarm.agents.orchestrator.runtime import RuntimeContext
from quanter_swarm.contracts import AgentContext, AgentResult, CycleReport


class RootAgent(BaseAgent):
    name = "root"
    role = "orchestrator"

    def __init__(self, runtime: RuntimeContext | None = None) -> None:
        self.runtime = runtime

    def run_sync(
        self,
        symbol: str | None = None,
        scenario: dict[str, Any] | None = None,
        provider_override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        result = CycleManager(provider_override=provider_override, runtime=self.runtime).run_cycle(
            symbol=symbol,
            scenario=scenario,
        )
        return CycleReport.model_validate(result).model_dump()

    def run_batch_sync(
        self,
        symbols: list[str],
        scenario: dict[str, Any] | None = None,
        provider_override: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        return [
            CycleReport.model_validate(result).model_dump()
            for result in CycleManager(provider_override=provider_override, runtime=self.runtime).run_cycle_batch(
                symbols=symbols,
                scenario=scenario,
            )
        ]

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self._context_to_dict(context)
        report = await asyncio.to_thread(
            self.run_sync,
            payload.get("symbol"),
            payload.get("scenario"),
        )
        return self._build_result(summary=str(report["active_regime"]), payload=report)
