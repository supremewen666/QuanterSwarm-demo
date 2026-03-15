"""Paper broker."""

from __future__ import annotations

from quanter_swarm.utils.ids import new_id


class PaperBroker:
    def submit(self, order: dict) -> dict:
        return {
            "status": "accepted",
            "order_id": new_id("paper"),
            "order": order,
            "fill_price": order.get("reference_price"),
        }
