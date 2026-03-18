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
        params = context.get("params", {})
        overshoot_threshold = float(params.get("overshoot_threshold", 0.55))
        reversal_window = float(params.get("reversal_window", 5))
        score = round(max(0.0, min(1.0, overshoot_threshold - trend * max(1.0, reversal_window * 0.8))), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "reversion_bias"}
