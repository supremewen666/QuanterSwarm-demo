"""Momentum leader."""

from quanter_swarm.leaders.base_leader import BaseLeader


class MomentumLeader(BaseLeader):
    name = "momentum"
    supported_regimes = ("trend_up", "risk_on", "high_vol")
    supported_tasks = ("trend_following", "breakout_confirmation")
    cost_hint = "medium"
    priority = 90

    def propose(self, context: dict) -> dict:
        trend = context["features"]["trend"]
        params = context.get("params", {})
        trend_strength_scale = float(params.get("trend_strength_scale", 5.0))
        volatility_penalty = float(params.get("volatility_penalty", 0.8))
        volatility = float(context["features"].get("volatility", 0.0))
        score = round(max(0.0, min(1.0, 0.5 + trend * trend_strength_scale - volatility * volatility_penalty)), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "trend_continuation"}
