from quanter_swarm.agents.orchestrator.states import (
    CycleStage,
    CycleState,
    StageRecord,
    state_for_stage,
)


def test_cycle_state_enum_matches_roadmap_states() -> None:
    assert CycleState.INIT.value == "init"
    assert CycleState.DATA_FETCH.value == "data_fetch"
    assert CycleState.REGIME_DETECT.value == "regime_detect"
    assert CycleState.ROUTING.value == "routing"
    assert CycleState.AGENT_EXECUTION.value == "agent_execution"
    assert CycleState.PORTFOLIO_BUILD.value == "portfolio_build"
    assert CycleState.RISK_CHECK.value == "risk_check"
    assert CycleState.REPORT_GENERATION.value == "report_generation"
    assert CycleState.DONE.value == "done"
    assert CycleState.FAILED.value == "failed"


def test_stage_record_derives_high_level_cycle_state() -> None:
    record = StageRecord(stage=CycleStage.ROUTE, status="ok", detail={"leaders": ["momentum"]})
    assert state_for_stage(CycleStage.INGEST) == CycleState.DATA_FETCH
    assert record.state == CycleState.ROUTING
