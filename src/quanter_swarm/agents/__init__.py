"""Agent interfaces."""

from quanter_swarm.agents.base import BaseAgent


def register_agent(agent_cls):
    from quanter_swarm.agents.registry import register_agent as _register_agent

    return _register_agent(agent_cls)


def get_agent(name: str, **kwargs):
    from quanter_swarm.agents.registry import get_agent as _get_agent

    return _get_agent(name, **kwargs)


def get_leader(name: str, **kwargs):
    from quanter_swarm.agents.registry import get_leader as _get_leader

    return _get_leader(name, **kwargs)


def get_specialist(name: str, **kwargs):
    from quanter_swarm.agents.registry import get_specialist as _get_specialist

    return _get_specialist(name, **kwargs)


def registry():
    from quanter_swarm.agents.registry import registry as _registry

    return _registry


__all__ = ["BaseAgent", "get_agent", "get_leader", "get_specialist", "register_agent", "registry"]
