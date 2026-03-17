from quanter_swarm.contracts import AgentContext, AgentResult, CycleReport, RouterDecision
from quanter_swarm.orchestrator.root_agent import RootAgent


def test_agent_schema_models_round_trip() -> None:
    context = AgentContext(symbol="AAPL", regime="trend_up", features={"momentum": 0.8})
    result = AgentResult(agent_name="momentum_leader", role="leader", payload={"score": 0.8})
    decision = RouterDecision(
        regime="trend_up",
        confidence=0.72,
        leader_selected=["momentum"],
        specialists_selected=["sentiment"],
        reasons={"momentum": "selected_by_regime_routing"},
        rejected_candidates={"mean_reversion": "removed_by_low_confidence_policy"},
    )

    assert context.symbol == "AAPL"
    assert result.agent_name == "momentum_leader"
    assert decision.leader_selected == ["momentum"]


def test_root_agent_returns_cycle_report_contract() -> None:
    report = RootAgent().run_sync("AAPL")
    validated = CycleReport.model_validate(report)

    assert validated.router_decision.regime == validated.active_regime
    assert validated.risk_check.status in {"pass", "reduced", "blocked"}
    assert validated.router_decision.reasons
    assert "budget_constraints" in validated.router_decision.model_dump()
