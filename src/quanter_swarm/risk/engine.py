"""Risk engine for portfolio-level trade approval."""

from __future__ import annotations

from typing import Any

from quanter_swarm.risk.rules import (
    earnings_no_trade_rule,
    max_daily_loss_rule,
    max_leverage_rule,
    max_position_size_rule,
    volatility_no_trade_rule,
)


def evaluate_risk_rules(
    *,
    portfolio: dict[str, Any],
    market_packet: dict[str, Any],
    event_payload: dict[str, Any],
    daily_loss_pct: float,
    rules_config: dict[str, Any],
) -> dict[str, Any]:
    triggered_rules = [
        rule
        for rule in (
            max_position_size_rule(portfolio, float(rules_config.get("max_position_size", 0.15))),
            max_leverage_rule(portfolio, float(rules_config.get("max_leverage", 1.0))),
            max_daily_loss_rule(daily_loss_pct, float(rules_config.get("max_daily_loss", 0.03))),
            earnings_no_trade_rule(event_payload, bool(rules_config.get("earnings_no_trade", True))),
            volatility_no_trade_rule(
                float(market_packet.get("volatility", 0.0)),
                float(rules_config.get("volatility_no_trade", 0.08)),
            ),
        )
        if rule is not None
    ]

    if triggered_rules:
        primary_reason = triggered_rules[0]
        return {
            "status": "blocked",
            "approved": False,
            "exposure_multiplier": 0.0,
            "reason": primary_reason,
            "warnings": triggered_rules,
            "triggered_rules": triggered_rules,
        }

    return {
        "status": "pass",
        "approved": True,
        "exposure_multiplier": 1.0,
        "reason": "risk_engine_approved",
        "warnings": [],
        "triggered_rules": [],
    }
