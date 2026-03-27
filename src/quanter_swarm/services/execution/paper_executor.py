"""Paper executor."""

from __future__ import annotations

from pathlib import Path

from quanter_swarm.services.execution.order_manager import OrderManager
from quanter_swarm.services.execution.paper_broker import PaperBroker


def execute(order: dict, config_dir: Path | None = None) -> dict:
    result = OrderManager(broker=PaperBroker(config_dir=config_dir)).submit(order)
    return {"executed": result["status"] in {"accepted", "partial"}, **result}
