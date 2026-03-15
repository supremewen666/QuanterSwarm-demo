from quanter_swarm.leaders.mean_reversion_leader import MeanReversionLeader


def test_mean_reversion_leader_name() -> None:
    assert MeanReversionLeader().name == "mean_reversion"
