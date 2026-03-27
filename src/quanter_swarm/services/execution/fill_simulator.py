"""Fill simulation with delay and partial fill semantics."""

from __future__ import annotations

from typing import Any

from quanter_swarm.backtest.execution_simulator import ExecutionSimulator


class FillSimulator:
    def __init__(self) -> None:
        self.simulator = ExecutionSimulator()

    def simulate(self, order: dict[str, Any]) -> dict[str, Any]:
        payload = self.simulator.simulate(order)
        payload["delayed"] = payload["status"] == "delayed"
        payload["partial_fill"] = payload["status"] == "partial"
        return payload
