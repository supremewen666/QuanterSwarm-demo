"""Event similarity helpers used by weak priors."""

from __future__ import annotations

from math import fabs
from typing import Any


def _categorical_similarity(left: Any, right: Any) -> float:
    if left is None or right is None:
        return 0.0
    return 1.0 if left == right else 0.0


def _numeric_similarity(left: float | None, right: float | None, scale: float) -> float:
    if left is None or right is None:
        return 0.0
    distance = fabs(float(left) - float(right))
    return max(0.0, 1.0 - min(1.0, distance / scale))


def event_similarity(current_event: dict[str, Any], historical_event: dict[str, Any]) -> dict[str, float]:
    semantic_similarity = (
        _categorical_similarity(current_event.get("event_type"), historical_event.get("event_type")) * 0.45
        + _categorical_similarity(current_event.get("impact"), historical_event.get("impact")) * 0.3
        + _categorical_similarity(current_event.get("symbol"), historical_event.get("symbol")) * 0.25
    )
    market_similarity = (
        _categorical_similarity(current_event.get("regime"), historical_event.get("regime")) * 0.55
        + _numeric_similarity(current_event.get("macro_risk"), historical_event.get("macro_risk"), 1.0) * 0.45
    )
    microstructure_similarity = (
        _numeric_similarity(current_event.get("trend"), historical_event.get("trend"), 0.25) * 0.5
        + _numeric_similarity(current_event.get("volatility"), historical_event.get("volatility"), 0.15) * 0.5
    )
    similarity = semantic_similarity * 0.35 + market_similarity * 0.35 + microstructure_similarity * 0.3
    return {
        "semantic_similarity": round(semantic_similarity, 4),
        "market_similarity": round(market_similarity, 4),
        "microstructure_similarity": round(microstructure_similarity, 4),
        "similarity": round(similarity, 4),
    }
