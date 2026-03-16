from quanter_swarm.orchestrator.cycle_manager import CycleManager


def _stage_names(report: dict) -> list[str]:
    stages = report["decision_trace_summary"]["state_machine"]["stages"]
    return [item["stage"] for item in stages]


def test_cycle_state_machine_has_expected_stages() -> None:
    report = CycleManager().run_cycle("AAPL", persist_outputs=False)
    names = _stage_names(report)
    for required in ("ingest", "regime", "route", "specialist_research", "leader_proposal", "rank", "risk", "allocate", "execute", "report"):
        assert required in names


def test_cycle_state_machine_short_circuit_no_data() -> None:
    report = CycleManager().run_cycle("AAPL", scenario={"force_no_data": True}, persist_outputs=False)
    machine = report["decision_trace_summary"]["state_machine"]
    assert machine["terminated"] is True
    assert machine["termination_reason"] == "no_data"
    assert report["portfolio_suggestion"]["mode"] == "no_trade"


def test_cycle_state_machine_short_circuit_low_confidence() -> None:
    manager = CycleManager()
    manager.router_config["low_confidence_policy"] = "no_trade"
    manager.router_config["confidence_threshold"] = 0.99
    report = manager.run_cycle("AAPL", persist_outputs=False)
    machine = report["decision_trace_summary"]["state_machine"]
    assert machine["terminated"] is True
    assert machine["termination_reason"] in {"low_confidence_no_trade", "no_trade"}
