"""Data provider abstraction for market inputs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from quanter_swarm.market.news_feed import fetch_news
from quanter_swarm.market.price_feed import get_latest_price as fetch_latest_price


class BaseDataProvider(ABC):
    data_source = "provider"

    @abstractmethod
    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        """Return recent price history for a symbol."""

    @abstractmethod
    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        """Return the latest market snapshot for a symbol."""

    @abstractmethod
    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        """Return recent news items for a symbol."""


class DeterministicDataProvider(BaseDataProvider):
    """Default provider backed by the deterministic local feeds."""

    data_source = "deterministic_local"

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        latest = self.get_latest_price(symbol)
        closes = list(latest.get("closes", []))[-lookback:]
        return [
            {"symbol": latest["symbol"], "close": close}
            for close in closes
        ]

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        return fetch_latest_price(symbol)

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return fetch_news(symbol)[:limit]


def get_default_data_provider() -> BaseDataProvider:
    return DeterministicDataProvider()
