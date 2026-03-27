"""Candidate ranking service."""

from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for item in candidates:
        posterior_raw = item.get("posterior_score")
        posterior = (
            _as_float(posterior_raw)
            if posterior_raw is not None
            else _as_float(item.get("score"))
            + _as_float(item.get("prior_score"))
            - _as_float(item.get("risk_penalty"))
            - _as_float(item.get("cost_penalty"))
        )
        composite = (
            posterior * 0.6
            + _as_float(item.get("regime_fit"), 0.5) * 0.25
            + (1 - _as_float(item.get("risk_penalty"))) * 0.15
        )
        enriched.append(
            {
                **item,
                "posterior_score": round(posterior, 4),
                "composite_rank_score": round(composite, 4),
            }
        )
    return sorted(enriched, key=lambda item: item.get("composite_rank_score", 0.0), reverse=True)
