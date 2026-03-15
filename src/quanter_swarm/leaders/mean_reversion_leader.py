"""Mean reversion leader."""

from quanter_swarm.leaders.base_leader import BaseLeader


class MeanReversionLeader(BaseLeader):
    name = "mean_reversion"

    def propose(self, context: dict) -> dict:
        trend = context["features"]["trend"]
        score = round(max(0.0, min(1.0, 0.55 - trend * 4)), 2)
        return {"leader": self.name, "symbol": context["symbol"], "score": score, "thesis": "reversion_bias"}
