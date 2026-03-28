"""Stable leader exports."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "BaseLeader": ("quanter_swarm.agents.leaders.base_leader", "BaseLeader"),
    "BreakoutEventLeader": ("quanter_swarm.agents.leaders.breakout_event_leader", "BreakoutEventLeader"),
    "MeanReversionLeader": ("quanter_swarm.agents.leaders.mean_reversion_leader", "MeanReversionLeader"),
    "MomentumLeader": ("quanter_swarm.agents.leaders.momentum_leader", "MomentumLeader"),
    "StatArbLeader": ("quanter_swarm.agents.leaders.stat_arb_leader", "StatArbLeader"),
    "get_leader": ("quanter_swarm.agents.leaders.leader_factory", "get_leader"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    return getattr(import_module(module_name), attribute)


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
