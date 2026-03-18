"""Candidate ranking."""

from __future__ import annotations


def rank_candidates(candidates: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for item in candidates:
        posterior = (
            item.get("posterior_score")
            if item.get("posterior_score") is not None
            else item.get("score", 0.0)
            + item.get("prior_score", 0.0)
            - item.get("risk_penalty", 0.0)
            - item.get("cost_penalty", 0.0)
        )
        composite = (
            posterior * 0.6
            + item.get("regime_fit", 0.5) * 0.25
            + (1 - item.get("risk_penalty", 0.0)) * 0.15
        )
        enriched.append({**item, "posterior_score": round(float(posterior), 4), "composite_rank_score": round(composite, 4)})
    return sorted(enriched, key=lambda item: item.get("composite_rank_score", 0.0), reverse=True)
