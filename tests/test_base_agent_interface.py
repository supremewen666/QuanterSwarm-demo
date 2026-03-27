import asyncio

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.agents.leaders.momentum_leader import MomentumLeader
from quanter_swarm.agents.orchestrator.root_agent import RootAgent
from quanter_swarm.agents.orchestrator.router_agent import RouterAgent
from quanter_swarm.agents.specialists.data_fetch_specialist import DataFetchSpecialist
from quanter_swarm.contracts import AgentContext


def test_leader_and_specialist_inherit_base_agent() -> None:
    assert isinstance(MomentumLeader(), BaseAgent)
    assert isinstance(DataFetchSpecialist(), BaseAgent)


def test_leader_run_returns_agent_result() -> None:
    result = asyncio.run(MomentumLeader().run(AgentContext(symbol="AAPL", features={"trend": 0.03})))
    assert result.agent_name == "momentum"
    assert result.role == "leader"
    assert result.payload["leader"] == "momentum"


def test_specialist_run_returns_agent_result() -> None:
    result = asyncio.run(DataFetchSpecialist().run({"symbol": "MSFT"}))
    assert result.agent_name == "data_fetch"
    assert result.role == "specialist"
    assert result.payload["symbol"] == "MSFT"


def test_router_agent_run_returns_agent_result() -> None:
    result = asyncio.run(
        RouterAgent().run(
            {
                "regime": {"label": "trend_up", "confidence": 0.8},
                "router_config": {"default_regime": "sideways"},
                "regimes_config": {"regimes": {"trend_up": {"leaders": ["momentum"]}}},
            }
        )
    )
    assert result.agent_name == "router"
    assert result.payload["leaders"] == ["momentum"]


def test_root_agent_run_returns_agent_result() -> None:
    result = asyncio.run(RootAgent().run({"symbol": "AAPL"}))
    assert result.agent_name == "root"
    assert result.role == "orchestrator"
    assert result.payload["symbol"] == "AAPL"
