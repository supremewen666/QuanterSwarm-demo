from quanter_swarm.leaders.stat_arb_leader import StatArbLeader


def test_stat_arb_leader_name() -> None:
    assert StatArbLeader().name == "stat_arb"
