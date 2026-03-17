"""Mean reversion leader."""

from quanter_swarm.leaders.base_leader import BaseLeader


class MeanReversionLeader(BaseLeader):
    name = "mean_reversion"
    supported_regimes = ("trend_down", "sideways", "risk_off")
    supported_tasks = ("mean_reversion", "defensive_rotation")
    cost_hint = "medium"
    priority = 80

    def propose(self, context: dict) -> dict:
        trend = context["features"]["trend"]
        score = round(max(0.0, min(1.0, 0.55 - trend * 4)), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "reversion_bias"}
