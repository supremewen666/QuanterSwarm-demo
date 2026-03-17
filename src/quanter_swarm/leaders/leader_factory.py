"""Leader factory."""

from quanter_swarm.agents.registry import get_leader as get_registered_leader


def get_leader(name: str):
    return get_registered_leader(name)
