"""Order submission facade with optional simulation."""

from __future__ import annotations

from typing import Any

from quanter_swarm.decision.paper_broker import PaperBroker
from quanter_swarm.execution.fill_simulator import FillSimulator


class OrderManager:
    def __init__(self, broker: PaperBroker | None = None, fill_simulator: FillSimulator | None = None) -> None:
        self.broker = broker or PaperBroker()
        self.fill_simulator = fill_simulator or FillSimulator()

    def submit(self, order: dict[str, Any]) -> dict[str, Any]:
        execution = self.broker.submit(order)
        simulation = self.fill_simulator.simulate(order)
        execution["simulation"] = simulation
        return execution
