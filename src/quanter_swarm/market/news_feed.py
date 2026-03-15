"""Deterministic news feed."""

from __future__ import annotations


def fetch_news(symbol: str) -> list[dict]:
    seed = sum(ord(char) for char in symbol.upper())
    if seed % 3 == 0:
        headlines = [
            "earnings outlook remains stable",
            "sector demand momentum updated",
        ]
    elif seed % 3 == 1:
        headlines = [
            "guidance revision highlights policy uncertainty",
            "input cost pressure remains elevated",
        ]
    else:
        headlines = [
            "new product cycle supports growth expectations",
            "management commentary signals disciplined execution",
        ]
    return [{"symbol": symbol.upper(), "headline": f"{symbol.upper()} {headline}"} for headline in headlines]
