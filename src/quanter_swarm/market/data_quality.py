"""Data quality validation helpers."""

from __future__ import annotations

from time import time


def validate_snapshot(snapshot: dict, staleness_sec: int = 3600) -> dict:
    issues: list[str] = []
    symbol = snapshot.get("symbol")
    as_of_ts = int(snapshot.get("as_of_ts", 0))
    market_packet = snapshot.get("market_packet", {})
    fundamentals_packet = snapshot.get("fundamentals_packet", {})
    available_at = snapshot.get("available_at")

    if not symbol:
        issues.append("missing_symbol")
    if not market_packet:
        issues.append("missing_market_packet")
    if not fundamentals_packet:
        issues.append("missing_fundamentals_packet")
    if as_of_ts <= 0 or int(time()) - as_of_ts > staleness_sec:
        issues.append("stale_snapshot")
    if symbol and fundamentals_packet and fundamentals_packet.get("symbol") != symbol:
        issues.append("symbol_mismatch")
    if float(market_packet.get("price", 0.0)) <= 0:
        issues.append("price_outlier")
    if len(snapshot.get("news_inputs", [])) == 0:
        issues.append("missing_news")
    if not available_at:
        issues.append("missing_available_at")
    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "freshness_sec": max(0, int(time()) - as_of_ts) if as_of_ts else None,
        "strict_backtest_eligible": available_at is not None and "missing_available_at" not in issues,
    }
