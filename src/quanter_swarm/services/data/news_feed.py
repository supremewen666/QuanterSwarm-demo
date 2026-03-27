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
    return [
        {
            "symbol": symbol.upper(),
            "headline": f"{symbol.upper()} {headline}",
            "body": f"{symbol.upper()} {headline}",
            "published_at": "2026-03-18T09:30:00+00:00",
            "ingested_at": "2026-03-18T09:31:00+00:00",
            "source": "deterministic_news",
            "publisher": "demo_wire",
            "url": f"demo://news/{symbol.lower()}",
            "language": "en",
            "event_type": "earnings" if "earnings" in headline else "company_update",
            "event_direction": "positive" if "supports" in headline or "stable" in headline else "neutral",
            "event_confidence": 0.65,
            "quality_flags": ["synthetic_source"],
        }
        for headline in headlines
    ]
