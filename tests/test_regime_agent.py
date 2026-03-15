from quanter_swarm.orchestrator.regime_agent import RegimeAgent


def test_regime_agent_classifies_market_state() -> None:
    assert RegimeAgent().classify({"avg_change_pct": -0.03, "volatility": 0.02, "macro_risk": 0.5}) == "trend_down"
