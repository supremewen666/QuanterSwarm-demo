from quanter_swarm.decision.execution_gate import execution_allowed


def test_execution_gate_blocks_live_mode() -> None:
    assert execution_allowed("live") == (False, "live_execution_blocked")
