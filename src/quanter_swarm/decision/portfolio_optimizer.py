"""Deterministic portfolio optimizer with interpretable penalties."""

from __future__ import annotations

from quanter_swarm.decision.risk_budgeting import apply_concentration_penalty


def _normalize(weights: dict[str, float], target_total: float) -> dict[str, float]:
    total = sum(max(0.0, value) for value in weights.values())
    if total <= 0:
        return {key: 0.0 for key in weights}
    return {key: round(max(0.0, value) / total * target_total, 6) for key, value in weights.items()}


def idea_utility(
    idea: dict,
    *,
    allocation_mode: str,
    correlation_penalty: float,
    turnover_penalty: float,
    event_penalty: float,
) -> float:
    score = float(idea.get("composite_rank_score", idea.get("score", 0.0)))
    confidence = float(idea.get("confidence", score))
    volatility = max(0.001, float(idea.get("volatility", 0.03)))
    correlation = float(idea.get("correlation", 0.3))
    turnover = max(0.0, float(idea.get("turnover", 0.0)))
    event_risk = max(0.0, float(idea.get("event_risk", 0.0)))

    base = score * confidence
    if allocation_mode in {"volatility_aware", "correlation_aware"}:
        base /= volatility
    if allocation_mode == "correlation_aware":
        base = apply_concentration_penalty(
            base,
            correlation=correlation,
            event_risk=event_risk,
            correlation_penalty=correlation_penalty,
            event_penalty=event_penalty,
        )
    turnover_discount = max(0.2, 1 - turnover_penalty * turnover)
    return round(max(0.0, base * turnover_discount), 6)


def optimize_weights(
    ideas: list[dict],
    *,
    gross_exposure: float,
    max_single_weight: float,
    allocation_mode: str,
    correlation_penalty: float,
    turnover_penalty: float,
    event_penalty: float,
) -> dict[str, float]:
    utility = {
        idea["leader"]: idea_utility(
            idea,
            allocation_mode=allocation_mode,
            correlation_penalty=correlation_penalty,
            turnover_penalty=turnover_penalty,
            event_penalty=event_penalty,
        )
        for idea in ideas
    }
    weighted = _normalize(utility, gross_exposure)
    capped = {leader: min(max_single_weight, weight) for leader, weight in weighted.items()}
    return _normalize(capped, min(gross_exposure, sum(capped.values())))
