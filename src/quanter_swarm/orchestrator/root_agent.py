"""Root orchestration entry point."""

from __future__ import annotations

from quanter_swarm.orchestrator.cycle_manager import CycleManager


class RootAgent:
    def run(self, symbol: str | None = None) -> dict:
        return CycleManager().run_cycle(symbol=symbol)
