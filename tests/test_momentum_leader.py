from quanter_swarm.agents.leaders.momentum_leader import MomentumLeader


def test_momentum_leader_name() -> None:
    assert MomentumLeader().name == "momentum"
