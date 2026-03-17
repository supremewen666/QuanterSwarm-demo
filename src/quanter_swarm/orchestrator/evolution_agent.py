"""Bounded evolution updates."""

from __future__ import annotations

from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentContext, AgentResult


class EvolutionAgent(BaseAgent):
    name = "evolution"
    role = "orchestrator"
    def evolve(self, ranked_signals: list[dict], current_threshold: float = 0.5) -> dict:
        if not ranked_signals:
            return {"threshold": current_threshold, "action": "hold"}

        leader_score = ranked_signals[0].get("composite_rank_score", 0.0)
        if leader_score > 0.65:
            return {"threshold": round(max(0.45, current_threshold - 0.02), 4), "action": "slightly_loosen"}
        if leader_score < 0.45:
            return {"threshold": round(min(0.6, current_threshold + 0.02), 4), "action": "slightly_tighten"}
        return {"threshold": current_threshold, "action": "hold"}

    async def run(self, context: AgentContext | dict[str, Any]) -> AgentResult:
        payload = self._context_to_dict(context)
        result = self.evolve(payload.get("ranked_signals", []), float(payload.get("current_threshold", 0.5)))
        return self._build_result(summary=str(result["action"]), payload=result)
