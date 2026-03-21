"""Data fetch specialist."""

from __future__ import annotations

from quanter_swarm.data.base import BaseDataProvider, get_default_data_provider
from quanter_swarm.data.cache import SnapshotCache
from quanter_swarm.specialists.base_specialist import BaseSpecialist
from quanter_swarm.tools.builtin import build_default_tool_registry
from quanter_swarm.tools.executor import ToolExecutor


class DataFetchSpecialist(BaseSpecialist):
    name = "data_fetch"
    supported_tasks = ("market_data", "fundamentals_fetch", "news_fetch")
    cost_hint = "high"
    priority = 100

    def __init__(
        self,
        provider: BaseDataProvider | None = None,
        cache: SnapshotCache | None = None,
        tool_executor: ToolExecutor | None = None,
    ) -> None:
        provider = provider or get_default_data_provider()
        super().__init__(tool_executor or ToolExecutor(build_default_tool_registry(provider=provider, cache=cache)))
        self.provider = provider or get_default_data_provider()
        self.cache = cache

    def fetch(self, symbol: str, use_cache: bool = True) -> dict:
        return self._run_tool("market_data", {"symbol": symbol, "use_cache": use_cache})

    def fetch_many(self, symbols: list[str], use_cache: bool = True) -> dict[str, dict]:
        snapshots = self._run_tool("market_data_batch", {"symbols": symbols, "use_cache": use_cache})
        return {symbol.upper(): snapshots[symbol.upper()] for symbol in symbols}

    def execute(self, payload: dict) -> dict:
        return self.fetch(str(payload["symbol"]))
