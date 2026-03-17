"""Primitive risk rules for pre-trade validation."""

from __future__ import annotations

from typing import Any


def max_position_size_rule(portfolio: dict[str, Any], threshold: float) -> str | None:
    for position in portfolio.get("positions", []):
        if float(position.get("weight", 0.0)) > threshold:
            return "max_position_size"
    return None


def max_leverage_rule(portfolio: dict[str, Any], threshold: float) -> str | None:
    if float(portfolio.get("gross_exposure", 0.0)) > threshold:
        return "max_leverage"
    return None


def max_daily_loss_rule(daily_loss_pct: float, threshold: float) -> str | None:
    if daily_loss_pct >= threshold:
        return "max_daily_loss"
    return None


def earnings_no_trade_rule(event_payload: dict[str, Any], enabled: bool) -> str | None:
    if not enabled:
        return None
    event_type = str(event_payload.get("event_type", "")).lower()
    if event_type == "earnings":
        return "earnings_no_trade"
    return None


def volatility_no_trade_rule(volatility: float, threshold: float) -> str | None:
    if volatility >= threshold:
        return "volatility_no_trade"
    return None
