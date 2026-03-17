import pytest

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.agents.registry import (
    AgentRegistry,
    get_agent,
    get_leader,
    get_specialist,
    registry,
)
from quanter_swarm.errors import RouterError


def test_registry_exposes_known_agents() -> None:
    assert "momentum" in registry.registered_names()
    assert "data_fetch" in registry.registered_names()
    assert get_leader("momentum").name == "momentum"
    assert get_specialist("data_fetch").name == "data_fetch"
    assert get_agent("router").name == "router"


def test_registry_rejects_unknown_agent() -> None:
    with pytest.raises(RouterError, match="Unknown agent"):
        get_agent("unknown")


def test_registry_rejects_wrong_role_lookup() -> None:
    with pytest.raises(RouterError, match="is not a leader"):
        get_leader("data_fetch")


def test_registry_allows_manual_registration() -> None:
    custom_registry = AgentRegistry()

    class DemoAgent(BaseAgent):
        name = "demo"
        role = "leader"

        async def run(self, context):
            return self._build_result(summary="demo", payload={"ok": True})

    custom_registry.register(DemoAgent)
    assert custom_registry.get_leader("demo").name == "demo"
