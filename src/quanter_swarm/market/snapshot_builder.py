"""Snapshot builder."""

from __future__ import annotations

from time import time

from quanter_swarm.market.fundamentals_feed import fetch_fundamentals
from quanter_swarm.market.macro_feed import fetch_macro_snapshot
from quanter_swarm.market.news_feed import fetch_news
from quanter_swarm.market.price_feed import get_latest_price


def build_snapshot(symbol: str) -> dict:
    market_packet = get_latest_price(symbol)
    fundamentals_packet = fetch_fundamentals(symbol)
    news_items = fetch_news(symbol)
    macro_inputs = fetch_macro_snapshot(symbol)
    return {
        "symbol": symbol.upper(),
        "as_of_ts": int(time()),
        "market_packet": {
            "symbol": market_packet["symbol"],
            "price": market_packet["price"],
            "closes": market_packet["closes"],
            "avg_volume": market_packet["avg_volume"],
            "change_pct": market_packet["change_pct"],
            "volatility": market_packet["volatility"],
        },
        "fundamentals_packet": fundamentals_packet,
        "news_inputs": [item["headline"] for item in news_items],
        "macro_inputs": macro_inputs,
    }
