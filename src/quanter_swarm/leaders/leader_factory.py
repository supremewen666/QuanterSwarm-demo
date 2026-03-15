"""Leader factory."""

from quanter_swarm.leaders.breakout_event_leader import BreakoutEventLeader
from quanter_swarm.leaders.mean_reversion_leader import MeanReversionLeader
from quanter_swarm.leaders.momentum_leader import MomentumLeader
from quanter_swarm.leaders.stat_arb_leader import StatArbLeader


def get_leader(name: str):
    leaders = {
        "momentum": MomentumLeader,
        "mean_reversion": MeanReversionLeader,
        "stat_arb": StatArbLeader,
        "breakout_event": BreakoutEventLeader,
    }
    return leaders[name]()
