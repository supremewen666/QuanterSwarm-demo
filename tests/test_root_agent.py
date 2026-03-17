from quanter_swarm.orchestrator.root_agent import RootAgent


def test_root_agent_runs_cycle() -> None:
    result = RootAgent().run_sync()
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
    assert "router_decision" in result
    assert "risk_check" in result
    assert result["decision_trace_summary"]["routing"]["leader_selected"] == result["router_decision"]["leader_selected"]
    assert "budget_constraints" in result["router_decision"]
    assert "specialist_rejections" in result["decision_trace_summary"]["routing"]
    assert result["decision_trace_summary"]["trace"]["risk_result"]["status"] == result["risk_check"]["status"]
    assert result["decision_trace_summary"]["state_machine"]["current_state"] == "done"
    assert all("state" in stage for stage in result["decision_trace_summary"]["state_machine"]["stages"])
    state_sequence = result["decision_trace_summary"]["state_machine"]["state_sequence"]
    assert state_sequence[0] == "init"
    assert "data_fetch" in state_sequence
    assert "regime_detect" in state_sequence
    assert "routing" in state_sequence
    assert "agent_execution" in state_sequence
    assert "risk_check" in state_sequence
    assert "portfolio_build" in state_sequence
    assert "report_generation" in state_sequence
    assert state_sequence[-1] == "done"
