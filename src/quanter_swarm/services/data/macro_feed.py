"""Deterministic macro feed."""

from __future__ import annotations


def fetch_macro_snapshot(symbol: str | None = None) -> dict:
    seed = sum(ord(char) for char in (symbol or "SPY").upper())
    macro_risk = round((seed % 9) / 10, 2)
    return {
        "macro_risk": macro_risk,
        "macro_theme": "disinflation" if seed % 2 == 0 else "policy_uncertainty",
        "observation_date": "2026-03-15",
        "release_time": "2026-03-16T12:30:00+00:00",
        "available_at": "2026-03-16T12:30:00+00:00",
        "source": "deterministic_macro",
    }
