"""Data fetch specialist."""

from __future__ import annotations

from quanter_swarm.market.snapshot_builder import build_snapshot
from quanter_swarm.specialists.base_specialist import BaseSpecialist


class DataFetchSpecialist(BaseSpecialist):
    name = "data_fetch"
    supported_tasks = ("market_data", "fundamentals_fetch", "news_fetch")
    cost_hint = "high"
    priority = 100

    def fetch(self, symbol: str) -> dict:
        return build_snapshot(symbol)

    def execute(self, payload: dict) -> dict:
        return self.fetch(str(payload["symbol"]))
