"""Bounded evolution updates."""

from __future__ import annotations


class EvolutionAgent:
    def evolve(self, ranked_signals: list[dict], current_threshold: float = 0.5) -> dict:
        if not ranked_signals:
            return {"threshold": current_threshold, "action": "hold"}

        leader_score = ranked_signals[0].get("composite_rank_score", 0.0)
        if leader_score > 0.65:
            return {"threshold": round(max(0.45, current_threshold - 0.02), 4), "action": "slightly_loosen"}
        if leader_score < 0.45:
            return {"threshold": round(min(0.6, current_threshold + 0.02), 4), "action": "slightly_tighten"}
        return {"threshold": current_threshold, "action": "hold"}
