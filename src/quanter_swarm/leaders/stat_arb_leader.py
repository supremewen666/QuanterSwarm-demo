"""Stat arb leader."""

from quanter_swarm.leaders.base_leader import BaseLeader


class StatArbLeader(BaseLeader):
    name = "stat_arb"
    supported_regimes = ("sideways", "risk_off", "trend_down")
    supported_tasks = ("relative_value", "pair_selection")
    cost_hint = "low"
    priority = 70

    def propose(self, context: dict) -> dict:
        quality = context["features"]["quality"]
        volatility = context["features"]["volatility"]
        score = round(max(0.0, min(1.0, 0.4 + quality * 0.1 - volatility)), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "relative_value"}
