"""Snapshot builder."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from time import time

from quanter_swarm.data.base import BaseDataProvider, get_default_data_provider
from quanter_swarm.market.fundamentals_feed import fetch_fundamentals
from quanter_swarm.market.macro_feed import fetch_macro_snapshot


def build_snapshot(symbol: str, provider: BaseDataProvider | None = None) -> dict:
    resolved_provider = provider or get_default_data_provider()
    as_of_ts = int(time())
    market_packet = resolved_provider.get_latest_price(symbol)
    price_history = resolved_provider.get_price_history(symbol)
    fundamentals_packet = fetch_fundamentals(symbol)
    news_items = resolved_provider.get_news(symbol)
    macro_inputs = fetch_macro_snapshot(symbol)
    snapshot = {
        "symbol": symbol.upper(),
        "as_of_ts": as_of_ts,
        "timestamp": datetime.fromtimestamp(as_of_ts, tz=UTC).isoformat(),
        "data_source": getattr(resolved_provider, "data_source", resolved_provider.__class__.__name__.lower()),
        "market_packet": {
            "symbol": market_packet["symbol"],
            "price": market_packet["price"],
            "closes": [row["close"] for row in price_history] or market_packet["closes"],
            "avg_volume": market_packet["avg_volume"],
            "change_pct": market_packet["change_pct"],
            "volatility": market_packet["volatility"],
        },
        "fundamentals_packet": fundamentals_packet,
        "news_inputs": [item["headline"] for item in news_items],
        "macro_inputs": macro_inputs,
    }
    snapshot["snapshot_hash"] = sha256(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return snapshot
