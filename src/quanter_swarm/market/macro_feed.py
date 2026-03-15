"""Deterministic macro feed."""

from __future__ import annotations


def fetch_macro_snapshot(symbol: str | None = None) -> dict:
    seed = sum(ord(char) for char in (symbol or "SPY").upper())
    macro_risk = round((seed % 9) / 10, 2)
    return {
        "macro_risk": macro_risk,
        "macro_theme": "disinflation" if seed % 2 == 0 else "policy_uncertainty",
    }
