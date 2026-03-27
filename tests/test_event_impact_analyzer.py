from quanter_swarm.services.research.event_impact_analyzer import analyze_event_impact


def test_event_impact_analyzer_returns_score() -> None:
    assert "impact_score" in analyze_event_impact({"event": "earnings"})
