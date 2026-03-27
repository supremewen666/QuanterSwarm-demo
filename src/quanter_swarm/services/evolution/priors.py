"""Weak prior aggregation over similar historical events."""

from __future__ import annotations

from math import exp
from typing import Any


def compute_weak_priors(
    similar_events: list[dict[str, Any]],
    *,
    target_regime: str,
    lambda_scale: float = 1.0,
) -> dict[str, dict[str, Any]]:
    priors: dict[str, dict[str, Any]] = {}
    for row in similar_events:
        leader = str(row.get("selected_leader", ""))
        if not leader:
            continue
        similarity = float(row.get("similarity", 0.0))
        prior_confidence = float(row.get("confidence", 0.5))
        samples = max(1, int(row.get("sample_count", 1)))
        regime_transferability = 1.0 if row.get("regime") == target_regime else 0.65
        recency_days = max(0.0, float(row.get("age_days", 0.0)))
        recency_decay = exp(-recency_days / 180)
        realized_outcome = float(row.get("realized_outcome", 0.0))
        contribution = (
            lambda_scale
            * similarity
            * prior_confidence
            * regime_transferability
            * recency_decay
            * realized_outcome
            * min(1.0, samples / 10)
        )
        bucket = priors.setdefault(
            leader,
            {"prior_score": 0.0, "sample_count": 0, "source_event_ids": [], "confidence": 0.0},
        )
        bucket["prior_score"] += contribution
        bucket["sample_count"] += samples
        bucket["confidence"] = max(bucket["confidence"], prior_confidence)
        if row.get("event_id"):
            bucket["source_event_ids"].append(row["event_id"])
    for payload in priors.values():
        payload["prior_score"] = round(payload["prior_score"], 4)
        payload["confidence"] = round(min(1.0, payload["confidence"]), 4)
        payload["source_event_ids"] = payload["source_event_ids"][:5]
    return priors
