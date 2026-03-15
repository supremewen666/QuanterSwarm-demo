"""Portfolio suggestion."""

from __future__ import annotations


def _normalize(weights: dict[str, float], target_total: float) -> dict[str, float]:
    total = sum(max(0.0, value) for value in weights.values())
    if total <= 0:
        return {key: 0.0 for key in weights}
    return {key: round(max(0.0, value) / total * target_total, 6) for key, value in weights.items()}


def _calc_weight_score(
    idea: dict,
    mode: str,
    correlation_penalty: float,
    turnover_penalty: float,
) -> float:
    score = float(idea.get("composite_rank_score", idea.get("score", 0.0)))
    confidence = float(idea.get("confidence", score))
    volatility = max(0.001, float(idea.get("volatility", 0.03)))
    correlation = max(0.0, min(1.0, float(idea.get("correlation", 0.3))))
    turnover = max(0.0, float(idea.get("turnover", 0.0)))
    if mode == "volatility_aware":
        return max(0.0, (score * confidence) / volatility)
    if mode == "correlation_aware":
        corr_discount = max(0.2, 1 - correlation_penalty * correlation)
        turnover_discount = max(0.2, 1 - turnover_penalty * turnover)
        return max(0.0, score * confidence * corr_discount * turnover_discount / volatility)
    return max(0.0, score * confidence)


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
) -> dict:
    active_overrides = (regime_overrides or {}).get(regime or "", {})
    effective_cash_buffer = float(active_overrides.get("cash_buffer", cash_buffer))
    effective_exposure_multiplier = float(active_overrides.get("exposure_multiplier", exposure_multiplier))
    effective_target_positions = int(active_overrides.get("target_positions", target_positions or len(ideas))) if ideas else 0
    tradable = [idea for idea in ideas if idea.get("score", 0.0) >= 0.5]
    if target_positions is not None:
        tradable = tradable[:target_positions]
    if effective_target_positions:
        tradable = tradable[:effective_target_positions]

    if not tradable or effective_exposure_multiplier <= 0:
        return {
            "positions": [],
            "cash_buffer": 1.0,
            "gross_exposure": 0.0,
            "mode": "no_trade",
            "allocation_mode": allocation_mode,
            "rationale": "no qualified ideas after risk review",
            "position_rationales": [],
        }

    gross_exposure = round(max(0.0, 1 - effective_cash_buffer) * min(effective_exposure_multiplier, 1.0), 4)
    raw_scores = {
        idea["leader"]: _calc_weight_score(idea, allocation_mode, correlation_penalty, turnover_penalty)
        for idea in tradable
    }
    weighted = _normalize(raw_scores, gross_exposure)
    capped = {leader: min(max_single_weight, weight) for leader, weight in weighted.items()}
    final_weights = _normalize(capped, min(gross_exposure, sum(capped.values())))

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
                    "volatility": round(float(idea.get("volatility", 0.03)), 4),
                    "correlation": round(float(idea.get("correlation", 0.3)), 4),
                    "allocation_mode": allocation_mode,
                },
            }
        )
    deployed = round(sum(position["weight"] for position in positions), 4)
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
