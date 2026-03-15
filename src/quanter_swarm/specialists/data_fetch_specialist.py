"""Data fetch specialist."""

from __future__ import annotations

from quanter_swarm.market.snapshot_builder import build_snapshot
from quanter_swarm.specialists.base_specialist import BaseSpecialist


class DataFetchSpecialist(BaseSpecialist):
    name = "data_fetch"

    def fetch(self, symbol: str) -> dict:
        return build_snapshot(symbol)
