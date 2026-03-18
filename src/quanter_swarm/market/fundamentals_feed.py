"""Deterministic fundamentals feed."""

from __future__ import annotations


def fetch_fundamentals(symbol: str) -> dict:
    seed = sum(ord(char) for char in symbol.upper())
    return {
        "symbol": symbol.upper(),
        "entity_id": f"entity-{symbol.upper()}",
        "fiscal_period": "FY",
        "period_end": "2025-12-31T00:00:00+00:00",
        "filed_at": "2026-02-15T21:00:00+00:00",
        "accepted_at": "2026-02-15T21:05:00+00:00",
        "available_at": "2026-02-15T21:05:00+00:00",
        "valuation": round((seed % 25) / 10, 2),
        "growth": round((seed % 18) / 10, 2),
        "quality": round((seed % 20) / 10, 2),
        "leverage": round((seed % 10) / 10, 2),
        "metric_name": "quality_blend",
        "metric_value": round((seed % 20) / 10, 2),
        "unit": "ratio",
        "source_doc": "demo://fundamentals",
        "source": "deterministic_fundamentals",
        "restatement_flag": False,
    }
