from quanter_swarm.services.reporting.report_generator import generate_report


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
            "router_decision": {
                "regime": "trend_up",
                "confidence": 0.72,
                "leader_selected": ["momentum"],
                "specialists_selected": ["sentiment"],
                "reasons": {"momentum": "selected_by_regime_routing"},
                "rejected_candidates": {},
            },
            "risk_check": {
                "status": "pass",
                "approved": True,
                "exposure_multiplier": 1.0,
                "reason": "approved",
                "warnings": [],
            },
            "portfolio_suggestion": {
                "positions": [],
                "mode": "paper",
                "gross_exposure": 0.0,
                "cash_buffer": 1.0,
                "allocation_mode": "simple",
                "rationale": "demo",
            },
            "paper_trade_actions": [],
            "decision_trace_summary": {"routing": {"low_confidence_mode": False}},
            "evidence_summary": {
                "data_sources": {
                    "market": {
                        "source": "polygon",
                        "available_at": "2026-03-18T09:30:00+00:00",
                        "reliability_score": 0.96,
                    }
                },
                "evolution": {
                    "action": "proposal_logged",
                    "top_posterior_leader": "momentum",
                    "parameter_version": "v1",
                    "prior_event_ids": ["evt-1"],
                },
            },
            "evaluation_summary": {"signal_count": 1},
        }
    )
    assert report["factor_scorecard"]["composite_score"] == 0.65
    assert report["symbol"] == "AAPL"
    assert report["regime_confidence"] == 0.72
    assert report["router_decision"]["regime"] == "trend_up"
    assert "# AAPL Research Cycle" in report["markdown_summary"]
    assert "## Architecture Layers" in report["markdown_summary"]
    assert "## Evidence" in report["markdown_summary"]
    assert report["architecture_summary"]["control_plane"]["router"]["selected_leaders"] == ["momentum"]
    assert report["evidence_summary"]["evolution"]["top_posterior_leader"] == "momentum"
