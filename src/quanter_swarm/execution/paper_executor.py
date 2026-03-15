"""Paper executor."""

from __future__ import annotations

from pathlib import Path

from quanter_swarm.decision.paper_broker import PaperBroker


def execute(order: dict, config_dir: Path | None = None) -> dict:
    result = PaperBroker(config_dir=config_dir).submit(order)
    return {"executed": result["status"] == "accepted", **result}
