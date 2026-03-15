"""Paper executor."""

from __future__ import annotations

from quanter_swarm.decision.paper_broker import PaperBroker


def execute(order: dict) -> dict:
    result = PaperBroker().submit(order)
    return {"executed": result["status"] == "accepted", **result}
