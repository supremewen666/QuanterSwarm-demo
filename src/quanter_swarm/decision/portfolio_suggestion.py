"""Portfolio suggestion."""

from __future__ import annotations

from quanter_swarm.decision.portfolio_optimizer import optimize_weights
from quanter_swarm.decision.risk_budgeting import resolve_regime_controls


def build_portfolio(
    ideas: list[dict],
    cash_buffer: float = 0.1,
    max_single_weight: float = 0.25,
    exposure_multiplier: float = 1.0,
    target_positions: int | None = None,
    allocation_mode: str = "simple",
    regime: str | None = None,
    regime_overrides: dict | None = None,
    correlation_penalty: float = 0.3,
    turnover_penalty: float = 0.15,
    event_penalty: float = 0.2,
    min_score: float = 0.35,
) -> dict:
    base_target = target_positions or len(ideas)
    controls = resolve_regime_controls(
        regime,
        base_cash_buffer=cash_buffer,
        base_exposure_multiplier=exposure_multiplier,
        base_target_positions=base_target,
        regime_overrides=regime_overrides,
    )
    effective_cash_buffer = float(controls["cash_buffer"])
    effective_exposure_multiplier = float(controls["exposure_multiplier"])
    effective_target_positions = int(controls["target_positions"])
    tradable = [idea for idea in ideas if float(idea.get("score", 0.0)) >= min_score]
    if effective_target_positions > 0:
        tradable = tradable[:effective_target_positions]

    if not tradable or effective_exposure_multiplier <= 0:
        return {
            "positions": [],
            "cash_buffer": 1.0,
            "gross_exposure": 0.0,
            "mode": "no_trade",
            "allocation_mode": allocation_mode,
            "rationale": "no qualified ideas after risk review",
            "no_trade_reason": "low_signal_or_blocked_exposure",
            "position_rationales": [],
        }

    gross_exposure = round(max(0.0, 1 - effective_cash_buffer) * min(effective_exposure_multiplier, 1.0), 4)
    final_weights = optimize_weights(
        tradable,
        gross_exposure=gross_exposure,
        max_single_weight=max_single_weight,
        allocation_mode=allocation_mode,
        correlation_penalty=correlation_penalty,
        turnover_penalty=turnover_penalty,
        event_penalty=event_penalty,
    )

    positions = []
    position_rationales = []
    for idea in tradable:
        leader = idea["leader"]
        weight = round(final_weights.get(leader, 0.0), 4)
        if weight <= 0:
            continue
        positions.append({"symbol": idea["symbol"], "leader": leader, "weight": weight})
        position_rationales.append(
            {
                "symbol": idea["symbol"],
                "leader": leader,
                "weight": weight,
                "reason": {
                    "score": round(float(idea.get("score", 0.0)), 4),
                    "confidence": round(float(idea.get("confidence", idea.get("score", 0.0))), 4),
                    "volatility": round(float(idea.get("volatility", 0.03)), 4),
                    "correlation": round(float(idea.get("correlation", 0.3)), 4),
                    "event_risk": round(float(idea.get("event_risk", 0.0)), 4),
                    "allocation_mode": allocation_mode,
                },
            }
        )
    deployed = round(sum(position["weight"] for position in positions), 4)
    if deployed <= 0:
        return {
            "positions": [],
            "cash_buffer": 1.0,
            "gross_exposure": 0.0,
            "mode": "no_trade",
            "allocation_mode": allocation_mode,
            "rationale": "all candidates scaled to zero after risk penalties",
            "no_trade_reason": "scaled_to_zero",
            "position_rationales": [],
        }
    mode = "reduced_exposure" if effective_exposure_multiplier < 1 else "paper"
    return {
        "positions": positions,
        "cash_buffer": round(1 - deployed, 4),
        "gross_exposure": deployed,
        "mode": mode,
        "allocation_mode": allocation_mode,
        "rationale": f"{allocation_mode} allocation with risk-adjusted exposure scaling",
        "position_rationales": position_rationales,
    }
