"""Momentum leader."""

from quanter_swarm.leaders.base_leader import BaseLeader


class MomentumLeader(BaseLeader):
    name = "momentum"

    def propose(self, context: dict) -> dict:
        trend = context["features"]["trend"]
        score = round(max(0.0, min(1.0, 0.5 + trend * 5)), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "trend_continuation"}
