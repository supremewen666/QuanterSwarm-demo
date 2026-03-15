from quanter_swarm.research.event_impact_analyzer import analyze_event_impact


def test_event_impact_analyzer_returns_score() -> None:
    assert "impact_score" in analyze_event_impact({"event": "earnings"})
