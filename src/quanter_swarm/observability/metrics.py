"""Cycle-level observability metrics."""

from __future__ import annotations

from typing import Any

from quanter_swarm.agents.registry import get_leader, get_specialist
from quanter_swarm.orchestrator.states import CycleState

_TOKEN_COST_BY_HINT = {
    "low": 800,
    "medium": 1800,
    "high": 3200,
}


def _state_key(state: CycleState) -> str:
    return state.value


def _estimated_tokens_for_agent(agent_name: str, role: str) -> int:
    if role == "leader":
        agent = get_leader(agent_name)
    else:
        agent = get_specialist(agent_name)
    cost_hint = getattr(agent, "cost_hint", "medium")
    return _TOKEN_COST_BY_HINT.get(str(cost_hint), _TOKEN_COST_BY_HINT["medium"])


def estimate_token_cost(
    *,
    leaders: list[str],
    specialists: list[str],
    token_budget: str | None = None,
) -> dict[str, Any]:
    leader_tokens = {
        leader: _estimated_tokens_for_agent(leader, "leader")
        for leader in leaders
    }
    specialist_tokens = {
        specialist: _estimated_tokens_for_agent(specialist, "specialist")
        for specialist in specialists
    }
    return {
        "estimated_tokens": sum(leader_tokens.values()) + sum(specialist_tokens.values()),
        "leaders": leader_tokens,
        "specialists": specialist_tokens,
        "budget": token_budget or "unknown",
    }


def build_cycle_metrics(
    *,
    state_latencies: dict[str, int],
    runtime_ms: int,
    leaders: list[str],
    specialists: list[str],
    success: bool,
    token_budget: str | None = None,
) -> dict[str, Any]:
    router_ms = state_latencies.get(_state_key(CycleState.ROUTING), 0)
    agent_latency = {
        "data_fetch_ms": state_latencies.get(_state_key(CycleState.DATA_FETCH), 0),
        "regime_detect_ms": state_latencies.get(_state_key(CycleState.REGIME_DETECT), 0),
        "agent_execution_ms": state_latencies.get(_state_key(CycleState.AGENT_EXECUTION), 0),
        "risk_check_ms": state_latencies.get(_state_key(CycleState.RISK_CHECK), 0),
        "portfolio_build_ms": state_latencies.get(_state_key(CycleState.PORTFOLIO_BUILD), 0),
        "report_generation_ms": state_latencies.get(_state_key(CycleState.REPORT_GENERATION), 0),
        "runtime_ms": runtime_ms,
    }
    return {
        "router_latency": {"routing_ms": router_ms},
        "agent_latency": agent_latency,
        "cycle_success_rate": {
            "value": 1.0 if success else 0.0,
            "successful_cycles": 1 if success else 0,
            "total_cycles": 1,
        },
        "token_cost": estimate_token_cost(
            leaders=leaders,
            specialists=specialists,
            token_budget=token_budget,
        ),
    }
