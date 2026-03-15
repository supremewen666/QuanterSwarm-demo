from quanter_swarm.orchestrator.root_agent import RootAgent


def test_root_agent_runs_cycle() -> None:
    result = RootAgent().run()
    assert result["active_regime"] in {
        "trend_up",
        "trend_down",
        "sideways",
        "high_vol",
        "panic",
        "risk_on",
        "risk_off",
    }
    assert "portfolio_suggestion" in result
