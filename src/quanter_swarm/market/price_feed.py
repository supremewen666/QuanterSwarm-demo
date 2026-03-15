"""Deterministic local price feed used for research and tests."""

from __future__ import annotations

from statistics import mean


def get_latest_price(symbol: str) -> dict:
    seed = sum(ord(char) for char in symbol.upper())
    drift = (seed % 5) - 1
    base_price = 95 + (seed % 17)
    closes = [round(base_price + step * drift, 2) for step in range(1, 6)]
    volumes = [1_000_000 + (seed % 100_000) + step * 10_000 for step in range(5)]
    price = float(closes[-1])
    previous_close = float(closes[0])
    change_pct = 0.0 if previous_close == 0 else (price - previous_close) / previous_close
    volatility = round(abs(change_pct) / 2 + (seed % 7) / 100, 4)
    return {
        "symbol": symbol.upper(),
        "price": price,
        "previous_close": previous_close,
        "closes": closes,
        "avg_volume": mean(volumes),
        "change_pct": round(change_pct, 4),
        "volatility": volatility,
    }
