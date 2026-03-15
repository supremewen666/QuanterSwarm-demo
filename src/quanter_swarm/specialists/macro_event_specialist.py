"""Macro event specialist."""

from quanter_swarm.specialists.base_specialist import BaseSpecialist


class MacroEventSpecialist(BaseSpecialist):
    name = "macro_event"

    def analyze(self, event: dict) -> dict:
        macro_risk = float(event.get("macro_risk", 0.0))
        direction = "negative" if macro_risk > 0.6 else "positive"
        return {"event": event, "impact": direction, "confidence": round(abs(0.5 - macro_risk) + 0.5, 2)}
