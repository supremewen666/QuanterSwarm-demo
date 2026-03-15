"""Feature engineering specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class FeatureEngineeringSpecialist(BaseSpecialist):
    name = "feature_engineering"

    def build(self, packet: dict) -> dict:
        market = packet.get("market_packet", {})
        fundamentals = packet.get("fundamentals_packet", {})
        trend = market.get("change_pct", 0.0)
        value = 1 / (1 + fundamentals.get("valuation", 1.0))
        quality = fundamentals.get("quality", 0.0)
        return {
            "features": {
                "trend": round(trend, 4),
                "value": round(value, 4),
                "quality": round(quality, 4),
                "volatility": market.get("volatility", 0.0),
            }
        }
