import asyncio
import time

import pytest

from quanter_swarm.agents.base import BaseAgent
from quanter_swarm.agents.orchestrator.agent_executor import AgentExecutor


class _SleepAgent(BaseAgent):
    role = "specialist"

    def __init__(self, name: str, delay: float) -> None:
        self.name = name
        self.delay = delay

    async def run(self, context):
        await asyncio.sleep(self.delay)
        return self._build_result(summary=self.name, payload={"context": context})


class _FailAgent(BaseAgent):
    name = "fail"
    role = "specialist"

    async def run(self, context):
        raise RuntimeError("boom")


def test_agent_executor_runs_jobs_concurrently() -> None:
    executor = AgentExecutor(timeout_seconds=1.0, allow_partial_failures=True)
    started = time.perf_counter()
    batch = executor.execute_many_sync(
        {
            "one": (_SleepAgent("one", 0.1), {"value": 1}),
            "two": (_SleepAgent("two", 0.1), {"value": 2}),
        }
    )
    elapsed = time.perf_counter() - started

    assert elapsed < 0.18
    assert set(batch.results) == {"one", "two"}
    assert not batch.failures


def test_agent_executor_records_partial_failures() -> None:
    executor = AgentExecutor(timeout_seconds=1.0, allow_partial_failures=True)
    batch = executor.execute_many_sync(
        {
            "ok": (_SleepAgent("ok", 0.0), {"value": 1}),
            "fail": (_FailAgent(), {"value": 2}),
        }
    )

    assert "ok" in batch.results
    assert batch.failures["fail"].error_type == "RuntimeError"


def test_agent_executor_enforces_timeout() -> None:
    executor = AgentExecutor(timeout_seconds=0.01, allow_partial_failures=True)
    batch = executor.execute_many_sync({"slow": (_SleepAgent("slow", 0.1), {})})
    assert batch.failures["slow"].error_type == "timeout"


def test_agent_executor_can_block_on_failures() -> None:
    executor = AgentExecutor(timeout_seconds=1.0, allow_partial_failures=False)
    with pytest.raises(Exception, match="Agent batch execution failed"):
        executor.execute_many_sync({"fail": (_FailAgent(), {})})
