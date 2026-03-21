"""Paper executor."""

from __future__ import annotations

from pathlib import Path

from quanter_swarm.decision.paper_broker import PaperBroker
from quanter_swarm.execution.order_manager import OrderManager


def execute(order: dict, config_dir: Path | None = None) -> dict:
    result = OrderManager(broker=PaperBroker(config_dir=config_dir)).submit(order)
    return {"executed": result["status"] in {"accepted", "partial"}, **result}
