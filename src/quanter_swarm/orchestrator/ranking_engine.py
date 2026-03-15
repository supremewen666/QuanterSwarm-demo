"""Candidate ranking."""

from __future__ import annotations


def rank_candidates(candidates: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for item in candidates:
        composite = (
            item.get("score", 0.0) * 0.6
            + item.get("regime_fit", 0.5) * 0.25
            + (1 - item.get("risk_penalty", 0.0)) * 0.15
        )
        enriched.append({**item, "composite_rank_score": round(composite, 4)})
    return sorted(enriched, key=lambda item: item.get("composite_rank_score", 0.0), reverse=True)
