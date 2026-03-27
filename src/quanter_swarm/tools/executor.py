"""Execution layer for tools with retries and timeouts."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from time import perf_counter
from typing import Any

from quanter_swarm.contracts import Status
from quanter_swarm.core.runtime.logging import get_logger
from quanter_swarm.tools.registry import ToolRegistry
from quanter_swarm.tools.schemas import ToolExecutionResult

logger = get_logger(__name__)


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
        *,
        timeout_seconds: float = 2.0,
        retries: int = 1,
    ) -> None:
        self.registry = registry
        self.timeout_seconds = timeout_seconds
        self.retries = retries

    def execute(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        tool = self.registry.get(tool_name)
        max_attempts = self.retries + 1
        start = perf_counter()
        for attempt in range(1, max_attempts + 1):
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(tool.run, **params)
                    payload = future.result(timeout=getattr(tool, "timeout_seconds", self.timeout_seconds))
                duration_ms = int((perf_counter() - start) * 1000)
                result = ToolExecutionResult(
                    tool_name=tool_name,
                    payload=payload,
                    attempts=attempt,
                    duration_ms=duration_ms,
                )
                logger.info("tool_execution_succeeded", extra=result.model_dump(mode="json"))
                return result.model_dump(mode="json")
            except FutureTimeoutError:
                error_type = "timeout"
                error_message = f"Tool '{tool_name}' timed out"
            except Exception as exc:  # pragma: no cover - covered via caller behavior
                error_type = type(exc).__name__
                error_message = str(exc)
            logger.warning(
                "tool_execution_failed",
                extra={
                    "tool_name": tool_name,
                    "attempt": attempt,
                    "error_type": error_type,
                    "error_message": error_message,
                },
            )
            if attempt == max_attempts:
                duration_ms = int((perf_counter() - start) * 1000)
                result = ToolExecutionResult(
                    tool_name=tool_name,
                    status=Status.ERROR,
                    reason=error_message,
                    confidence=0.0,
                    attempts=attempt,
                    duration_ms=duration_ms,
                    error_type=error_type,
                )
                return result.model_dump(mode="json")
        raise RuntimeError("unreachable")
