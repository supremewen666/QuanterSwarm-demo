from quanter_swarm.orchestrator.regime_agent import RegimeAgent


def test_regime_agent_classifies_market_state() -> None:
    assert RegimeAgent().classify({"avg_change_pct": -0.03, "volatility": 0.02, "macro_risk": 0.5}) == "trend_down"


def test_regime_agent_returns_detail_with_confidence() -> None:
    detail = RegimeAgent().classify_detail({"avg_change_pct": 0.01, "volatility": 0.03, "macro_risk": 0.4})
    assert detail["label"] in {"trend_up", "sideways", "risk_on", "high_vol"}
    assert 0.0 <= detail["confidence"] <= 1.0
    assert "supporting_features" in detail


def test_regime_agent_supports_hysteresis() -> None:
    detail = RegimeAgent().classify_detail(
        {"avg_change_pct": 0.001, "volatility": 0.02, "macro_risk": 0.48},
        previous_regime="risk_off",
        hysteresis_margin=10.0,
    )
    assert detail["label"] == "risk_off"
    assert detail["smoothing_applied"] is True
