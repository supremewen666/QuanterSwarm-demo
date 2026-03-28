from quanter_swarm.agents.leaders import MeanReversionLeader


def test_mean_reversion_leader_name() -> None:
    assert MeanReversionLeader().name == "mean_reversion"
