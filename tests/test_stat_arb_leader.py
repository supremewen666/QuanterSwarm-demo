from quanter_swarm.agents.leaders import StatArbLeader


def test_stat_arb_leader_name() -> None:
    assert StatArbLeader().name == "stat_arb"
