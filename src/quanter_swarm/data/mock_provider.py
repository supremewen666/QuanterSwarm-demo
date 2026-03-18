"""In-memory data provider for tests and experiments."""

from __future__ import annotations

from typing import Any

from quanter_swarm.data.base import BaseDataProvider


class MockDataProvider(BaseDataProvider):
    data_source = "mock"
    source_type = "mock"

    def __init__(
        self,
        *,
        latest_prices: dict[str, dict[str, Any]] | None = None,
        price_history: dict[str, list[dict[str, Any]]] | None = None,
        news: dict[str, list[dict[str, Any]]] | None = None,
    ) -> None:
        self._latest_prices = {symbol.upper(): payload for symbol, payload in (latest_prices or {}).items()}
        self._price_history = {symbol.upper(): payload for symbol, payload in (price_history or {}).items()}
        self._news = {symbol.upper(): payload for symbol, payload in (news or {}).items()}

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        return list(self._price_history.get(symbol.upper(), []))[-lookback:]

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        return dict(self._latest_prices[symbol.upper()])

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return list(self._news.get(symbol.upper(), []))[:limit]
