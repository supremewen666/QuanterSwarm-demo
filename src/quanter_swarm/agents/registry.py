"""Central agent registry."""

from __future__ import annotations

from typing import TypeVar

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.errors import RouterError
from quanter_swarm.leaders.breakout_event_leader import BreakoutEventLeader
from quanter_swarm.leaders.mean_reversion_leader import MeanReversionLeader
from quanter_swarm.leaders.momentum_leader import MomentumLeader
from quanter_swarm.leaders.stat_arb_leader import StatArbLeader
from quanter_swarm.orchestrator.evolution_agent import EvolutionAgent
from quanter_swarm.orchestrator.regime_agent import RegimeAgent
from quanter_swarm.orchestrator.router_agent import RouterAgent
from quanter_swarm.specialists.data_fetch_specialist import DataFetchSpecialist
from quanter_swarm.specialists.feature_engineering_specialist import FeatureEngineeringSpecialist
from quanter_swarm.specialists.macro_event_specialist import MacroEventSpecialist
from quanter_swarm.specialists.memory_compression_specialist import MemoryCompressionSpecialist
from quanter_swarm.specialists.risk_specialist import RiskSpecialist
from quanter_swarm.specialists.sentiment_specialist import SentimentSpecialist

AgentType = TypeVar("AgentType", bound=BaseAgent)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, type[BaseAgent]] = {}

    def register(self, agent_cls: type[BaseAgent]) -> None:
        name = getattr(agent_cls, "name", "").strip()
        if not name:
            raise RouterError(f"Cannot register unnamed agent class: {agent_cls!r}")
        self._agents[name] = agent_cls

    def create(self, name: str) -> BaseAgent:
        try:
            agent_cls = self._agents[name]
        except KeyError as exc:
            raise RouterError(f"Unknown agent '{name}'") from exc
        return agent_cls()

    def get_leader(self, name: str) -> BaseAgent:
        agent = self.create(name)
        if agent.role != "leader":
            raise RouterError(f"Agent '{name}' is not a leader.")
        return agent

    def get_specialist(self, name: str) -> BaseAgent:
        agent = self.create(name)
        if agent.role != "specialist":
            raise RouterError(f"Agent '{name}' is not a specialist.")
        return agent

    def registered_names(self) -> list[str]:
        return sorted(self._agents)


registry = AgentRegistry()
for agent_cls in (
    MomentumLeader,
    MeanReversionLeader,
    StatArbLeader,
    BreakoutEventLeader,
    DataFetchSpecialist,
    MemoryCompressionSpecialist,
    RiskSpecialist,
    SentimentSpecialist,
    MacroEventSpecialist,
    FeatureEngineeringSpecialist,
    RegimeAgent,
    RouterAgent,
    EvolutionAgent,
):
    registry.register(agent_cls)


def register_agent(agent_cls: type[BaseAgent]) -> None:
    registry.register(agent_cls)


def get_agent(name: str) -> BaseAgent:
    return registry.create(name)


def get_leader(name: str) -> BaseAgent:
    return registry.get_leader(name)


def get_specialist(name: str) -> BaseAgent:
    return registry.get_specialist(name)
