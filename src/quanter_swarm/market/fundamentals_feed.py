"""Deterministic fundamentals feed."""

from __future__ import annotations


def fetch_fundamentals(symbol: str) -> dict:
    seed = sum(ord(char) for char in symbol.upper())
    return {
        "symbol": symbol.upper(),
        "valuation": round((seed % 25) / 10, 2),
        "growth": round((seed % 18) / 10, 2),
        "quality": round((seed % 20) / 10, 2),
        "leverage": round((seed % 10) / 10, 2),
    }
