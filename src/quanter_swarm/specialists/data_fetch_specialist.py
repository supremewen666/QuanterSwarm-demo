"""Data fetch specialist."""

from __future__ import annotations

from quanter_swarm.data.base import BaseDataProvider, get_default_data_provider
from quanter_swarm.data.cache import SnapshotCache
from quanter_swarm.market.snapshot_builder import build_snapshot
from quanter_swarm.specialists.base_specialist import BaseSpecialist


class DataFetchSpecialist(BaseSpecialist):
    name = "data_fetch"
    supported_tasks = ("market_data", "fundamentals_fetch", "news_fetch")
    cost_hint = "high"
    priority = 100

    def __init__(
        self,
        provider: BaseDataProvider | None = None,
        cache: SnapshotCache | None = None,
    ) -> None:
        self.provider = provider or get_default_data_provider()
        self.cache = cache

    def fetch(self, symbol: str, use_cache: bool = True) -> dict:
        cache_key = symbol.upper()
        if use_cache and self.cache is not None:
            cached = self.cache.get_snapshot(cache_key)
            if cached is not None:
                cached["cache_hit"] = True
                return cached
        snapshot = build_snapshot(symbol, provider=self.provider)
        if self.cache is not None:
            self.cache.set_snapshot(cache_key, snapshot)
        return snapshot

    def execute(self, payload: dict) -> dict:
        return self.fetch(str(payload["symbol"]))
