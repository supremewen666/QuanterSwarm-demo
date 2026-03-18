"""Feature engineering specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class FeatureEngineeringSpecialist(BaseSpecialist):
    name = "feature_engineering"
    supported_tasks = ("feature_engineering", "signal_features")
    cost_hint = "medium"
    priority = 85

    def build(self, packet: dict) -> dict:
        market = packet.get("market_packet", {})
        fundamentals = packet.get("fundamentals_packet", {})
        shares_float = packet.get("shares_float_packet", {})
        trend = market.get("change_pct", 0.0)
        value = 1 / (1 + fundamentals.get("valuation", 1.0))
        quality = fundamentals.get("quality", 0.0)
        avg_volume = float(market.get("avg_volume", 0.0) or 0.0)
        float_shares = float(shares_float.get("float_shares", 0.0) or 0.0)
        float_turnover = 0.0 if float_shares <= 0 else min(1.0, avg_volume / float_shares)
        crowding = 1.0 - float_turnover if float_turnover > 0 else 0.5
        return {
            "features": {
                "trend": round(trend, 4),
                "value": round(value, 4),
                "quality": round(quality, 4),
                "volatility": market.get("volatility", 0.0),
                "float_turnover": round(float_turnover, 4),
                "crowding": round(crowding, 4),
            }
        }

    def execute(self, payload: dict) -> dict:
        return self.build(payload)
