"""Data provider abstraction for market inputs."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, cast

from quanter_swarm.market.news_feed import fetch_news
from quanter_swarm.market.price_feed import get_latest_price as fetch_latest_price


class BaseDataProvider(ABC):
    data_source = "provider"
    source_type = "derived"

    @abstractmethod
    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        """Return recent price history for a symbol."""

    @abstractmethod
    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        """Return the latest market snapshot for a symbol."""

    @abstractmethod
    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        """Return recent news items for a symbol."""

    def get_latest_prices(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_latest_price(symbol) for symbol in symbols}

    def get_price_histories(self, symbols: list[str], lookback: int = 5) -> dict[str, list[dict[str, Any]]]:
        return {symbol.upper(): self.get_price_history(symbol, lookback=lookback) for symbol in symbols}

    def get_news_batch(self, symbols: list[str], limit: int = 5) -> dict[str, list[dict[str, Any]]]:
        return {symbol.upper(): self.get_news(symbol, limit=limit) for symbol in symbols}

    def get_fundamentals(self, symbol: str) -> dict[str, Any]:
        from quanter_swarm.market.fundamentals_feed import fetch_fundamentals

        return fetch_fundamentals(symbol)

    def get_fundamentals_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_fundamentals(symbol) for symbol in symbols}

    def get_macro(self, symbol: str) -> dict[str, Any]:
        from quanter_swarm.market.macro_feed import fetch_macro_snapshot

        return fetch_macro_snapshot(symbol)

    def get_macro_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_macro(symbol) for symbol in symbols}

    def get_shares_float(self, symbol: str) -> dict[str, Any]:
        return {}

    def get_shares_float_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_shares_float(symbol) for symbol in symbols}

    def get_filings(self, symbol: str, limit: int = 10) -> list[dict[str, Any]]:
        return []

    def get_filings_batch(self, symbols: list[str], limit: int = 10) -> dict[str, list[dict[str, Any]]]:
        return {symbol.upper(): self.get_filings(symbol, limit=limit) for symbol in symbols}

    def get_xbrl_facts(self, symbol: str) -> list[dict[str, Any]]:
        return []

    def get_xbrl_facts_batch(self, symbols: list[str]) -> dict[str, list[dict[str, Any]]]:
        return {symbol.upper(): self.get_xbrl_facts(symbol) for symbol in symbols}

    def get_macro_vintages(self, symbol: str) -> list[dict[str, Any]]:
        return []

    def get_macro_vintages_batch(self, symbols: list[str]) -> dict[str, list[dict[str, Any]]]:
        return {symbol.upper(): self.get_macro_vintages(symbol) for symbol in symbols}


class DeterministicDataProvider(BaseDataProvider):
    """Default provider backed by the deterministic local feeds."""

    data_source = "deterministic_local"
    source_type = "synthetic"

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        latest = self.get_latest_price(symbol)
        closes = list(latest.get("closes", []))[-lookback:]
        return [
            {"symbol": latest["symbol"], "close": close}
            for close in closes
        ]

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        payload = fetch_latest_price(symbol)
        payload.setdefault("ts_event", datetime.now(tz=UTC).isoformat())
        payload.setdefault("ts_available", payload["ts_event"])
        payload.setdefault("vendor_symbol", symbol.upper())
        payload.setdefault("quality_flags", ["synthetic_source"])
        return payload

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return fetch_news(symbol)[:limit]


def get_default_data_provider() -> BaseDataProvider:
    provider_name = os.getenv("QUANTER_DATA_PROVIDER", "").strip()
    if provider_name:
        from quanter_swarm.data.registry import create_provider

        kwargs = {
            key.removeprefix("QUANTER_PROVIDER_").lower(): value
            for key, value in os.environ.items()
            if key.startswith("QUANTER_PROVIDER_")
        }
        return cast(BaseDataProvider, create_provider(provider_name, **kwargs))
    return DeterministicDataProvider()
