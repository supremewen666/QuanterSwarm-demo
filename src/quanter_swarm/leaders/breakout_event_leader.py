"""Breakout event leader."""

from quanter_swarm.leaders.base_leader import BaseLeader


class BreakoutEventLeader(BaseLeader):
    name = "breakout_event"
    supported_regimes = ("trend_up", "high_vol", "panic", "risk_on")
    supported_tasks = ("event_breakout", "catalyst_response")
    cost_hint = "high"
    priority = 95

    def propose(self, context: dict) -> dict:
        trend = context["features"]["trend"]
        event_boost = 0.15 if context.get("event_impact", {}).get("impact") == "positive" else -0.05
        score = round(max(0.0, min(1.0, 0.45 + trend * 3 + event_boost)), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "breakout_with_catalyst"}
