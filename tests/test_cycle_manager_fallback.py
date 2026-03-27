from quanter_swarm.agents.orchestrator.cycle_manager import CycleManager


def test_cycle_manager_records_specialist_fallback_modes() -> None:
    report = CycleManager().run_cycle("AAPL", scenario={"disable_specialists": {"sentiment": True}}, persist_outputs=False)
    fallback_modes = report["decision_trace_summary"]["fallback_modes"]
    assert "sentiment_fallback" in fallback_modes
