"""Event impact analysis."""


def analyze_event_impact(event: dict) -> dict:
    impact = event.get("impact", "neutral")
    impact_score = {"positive": 0.7, "negative": 0.3}.get(impact, 0.5)
    return {"event": event, "impact_score": impact_score, "horizon": "1d-1w"}
