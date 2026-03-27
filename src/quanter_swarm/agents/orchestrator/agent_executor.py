"""Concurrent agent execution helpers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.contracts import AgentResult
from quanter_swarm.errors import AgentExecutionError


@dataclass
class ExecutionFailure:
    error_type: str
    message: str


@dataclass
class ExecutionBatch:
    results: dict[str, AgentResult] = field(default_factory=dict)
    failures: dict[str, ExecutionFailure] = field(default_factory=dict)


class AgentExecutor:
    def __init__(self, timeout_seconds: float = 1.0, allow_partial_failures: bool = True) -> None:
        self.timeout_seconds = timeout_seconds
        self.allow_partial_failures = allow_partial_failures

    async def _run_one(self, name: str, agent: BaseAgent, context: dict[str, Any]) -> tuple[str, AgentResult | ExecutionFailure]:
        try:
            result = await asyncio.wait_for(agent.run(context), timeout=self.timeout_seconds)
            return name, result
        except TimeoutError:
            return name, ExecutionFailure(error_type="timeout", message=f"Agent '{name}' timed out")
        except Exception as exc:  # pragma: no cover - exercised through tests
            return name, ExecutionFailure(error_type=type(exc).__name__, message=str(exc))

    async def execute_many(self, jobs: dict[str, tuple[BaseAgent, dict[str, Any]]]) -> ExecutionBatch:
        pairs = await asyncio.gather(*(self._run_one(name, agent, context) for name, (agent, context) in jobs.items()))
        batch = ExecutionBatch()
        for name, outcome in pairs:
            if isinstance(outcome, AgentResult):
                batch.results[name] = outcome
            else:
                batch.failures[name] = outcome

        if batch.failures and not self.allow_partial_failures:
            failure_messages = ", ".join(f"{name}: {failure.message}" for name, failure in sorted(batch.failures.items()))
            raise AgentExecutionError(f"Agent batch execution failed: {failure_messages}")
        return batch

    def execute_many_sync(self, jobs: dict[str, tuple[BaseAgent, dict[str, Any]]]) -> ExecutionBatch:
        return asyncio.run(self.execute_many(jobs))
