from quanter_swarm.reporting.report_generator import generate_report


def test_report_generator_returns_summary() -> None:
    report = generate_report(
        {
            "symbol": "AAPL",
            "active_regime": "trend_up",
            "regime_confidence": 0.72,
            "active_strategy_teams": ["momentum"],
            "market_summary": {"price": 100},
            "fundamentals_summary": {"quality_score": 0.7},
            "sentiment_summary": {"score": 0.6},
            "event_impact_summary": {"impact_score": 0.7},
            "factor_score": 0.65,
            "risk_alerts": [],
            "portfolio_suggestion": {"positions": [], "mode": "paper"},
            "paper_trade_actions": [],
            "decision_trace_summary": {"routing": {"low_confidence_mode": False}},
            "evaluation_summary": {"signal_count": 1},
        }
    )
    assert report["factor_scorecard"]["composite_score"] == 0.65
    assert report["symbol"] == "AAPL"
    assert report["regime_confidence"] == 0.72
    assert "# AAPL Research Cycle" in report["markdown_summary"]
