from quanter_swarm.agents.leaders import BreakoutEventLeader


def test_breakout_event_leader_name() -> None:
    assert BreakoutEventLeader().name == "breakout_event"
