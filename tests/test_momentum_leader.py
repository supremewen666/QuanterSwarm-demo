from quanter_swarm.agents.leaders import MomentumLeader


def test_momentum_leader_name() -> None:
    assert MomentumLeader().name == "momentum"
