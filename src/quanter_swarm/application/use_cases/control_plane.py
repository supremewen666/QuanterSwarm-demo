"""Control-plane use cases exposed to external adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quanter_swarm.agents.orchestrator import RootAgent, RuntimeContext
from quanter_swarm.application.use_cases.common import provider_override
from quanter_swarm.core import CycleReport


@dataclass(slots=True)
class RunResearchCycle:
    """Execute one orchestrated research cycle through the application layer."""

    runtime: RuntimeContext | None = None

    def execute(
        self,
        *,
        symbol: str,
        scenario: dict[str, Any] | None = None,
        data_provider: str | None = None,
    ) -> dict[str, Any]:
        report = RootAgent(runtime=self.runtime).run_sync(
            symbol=symbol,
            scenario=scenario,
            provider_override=provider_override(data_provider),
        )
        return CycleReport.model_validate(report).model_dump()


@dataclass(slots=True)
class RunBatchResearch:
    """Execute a batch of orchestrated research cycles through the application layer."""

    runtime: RuntimeContext | None = None

    def execute(
        self,
        *,
        symbols: list[str],
        scenario: dict[str, Any] | None = None,
        data_provider: str | None = None,
    ) -> list[dict[str, Any]]:
        root_agent = RootAgent(runtime=self.runtime)
        return [
            CycleReport.model_validate(report).model_dump()
            for report in root_agent.run_batch_sync(
                symbols=symbols,
                scenario=scenario,
                provider_override=provider_override(data_provider),
            )
        ]
