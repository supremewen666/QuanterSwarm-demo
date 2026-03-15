"""Regime classifier."""

from __future__ import annotations


class RegimeAgent:
    def classify_detail(
        self,
        market_state: dict,
        previous_regime: str | None = None,
        hysteresis_margin: float = 0.08,
    ) -> dict:
        avg_change = float(market_state.get("avg_change_pct", 0.0))
        volatility = float(market_state.get("volatility", 0.0))
        macro_risk = float(market_state.get("macro_risk", 0.0))
        breadth = float(market_state.get("breadth", 0.5))
        dispersion = float(market_state.get("dispersion", volatility))
        correlation = float(market_state.get("correlation", 0.5))
        volume_anomaly = float(market_state.get("volume_anomaly", 0.0))
        event_density = float(market_state.get("event_density", 0.0))
        trend_strength = abs(avg_change)

        candidates = {
            "panic": 0.35 * min(1.0, volatility / 0.06)
            + 0.25 * min(1.0, max(0.0, -avg_change) / 0.03)
            + 0.2 * macro_risk
            + 0.2 * event_density,
            "high_vol": 0.45 * min(1.0, volatility / 0.05)
            + 0.2 * min(1.0, dispersion / 0.05)
            + 0.15 * volume_anomaly
            + 0.2 * correlation,
            "risk_off": 0.4 * macro_risk
            + 0.2 * min(1.0, max(0.0, -avg_change) / 0.03)
            + 0.2 * correlation
            + 0.2 * (1.0 - breadth),
            "trend_up": 0.45 * min(1.0, max(0.0, avg_change) / 0.03)
            + 0.2 * trend_strength
            + 0.2 * breadth
            + 0.15 * (1.0 - macro_risk),
            "trend_down": 0.45 * min(1.0, max(0.0, -avg_change) / 0.03)
            + 0.2 * trend_strength
            + 0.2 * (1.0 - breadth)
            + 0.15 * macro_risk,
            "risk_on": 0.35 * (1.0 - macro_risk)
            + 0.25 * max(0.0, avg_change)
            + 0.2 * breadth
            + 0.2 * (1.0 - correlation),
            "sideways": 0.4 * (1.0 - min(1.0, trend_strength / 0.03))
            + 0.2 * (1.0 - min(1.0, volatility / 0.05))
            + 0.2 * (1.0 - dispersion)
            + 0.2 * (1.0 - event_density),
        }
        sorted_candidates = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
        best_label, best_score = sorted_candidates[0]
        alt_label, alt_score = sorted_candidates[1]
        confidence = round(max(0.05, min(0.99, best_score - alt_score + 0.5)), 2)

        smoothing_applied = False
        if previous_regime and previous_regime != best_label and (best_score - alt_score) < hysteresis_margin:
            best_label = previous_regime
            smoothing_applied = True
            confidence = round(max(0.05, confidence - 0.08), 2)

        return {
            "label": best_label,
            "confidence": confidence,
            "supporting_features": {
                "trend_strength": round(trend_strength, 4),
                "volatility": round(volatility, 4),
                "correlation": round(correlation, 4),
                "dispersion": round(dispersion, 4),
                "breadth": round(breadth, 4),
                "volume_anomaly": round(volume_anomaly, 4),
                "event_density": round(event_density, 4),
                "macro_risk": round(macro_risk, 4),
            },
            "alternatives": [
                {"label": label, "score": round(score, 4)}
                for label, score in sorted_candidates[1:3]
            ],
            "smoothing_applied": smoothing_applied,
        }

    def classify(self, market_state: dict, previous_regime: str | None = None) -> str:
        return self.classify_detail(market_state, previous_regime=previous_regime)["label"]
