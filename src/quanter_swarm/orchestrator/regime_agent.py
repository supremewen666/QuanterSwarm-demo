"""Regime classifier."""


class RegimeAgent:
    def classify(self, market_state: dict) -> str:
        avg_change = float(market_state.get("avg_change_pct", 0.0))
        volatility = float(market_state.get("volatility", 0.0))
        macro_risk = float(market_state.get("macro_risk", 0.0))

        if volatility >= 0.045 and avg_change <= -0.02:
            return "panic"
        if volatility >= 0.035:
            return "high_vol"
        if macro_risk >= 0.7 and avg_change < 0:
            return "risk_off"
        if avg_change >= 0.025:
            return "trend_up"
        if avg_change <= -0.025:
            return "trend_down"
        if macro_risk <= 0.3 and avg_change > 0:
            return "risk_on"
        return "sideways"
