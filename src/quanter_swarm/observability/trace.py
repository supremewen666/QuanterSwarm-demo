"""Structured trace helpers for cycle execution."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


def new_trace_id(prefix: str = "trace") -> str:
    return f"{prefix}_{uuid4().hex}"


def build_cycle_trace(
    *,
    trace_id: str,
    router_decision: dict[str, Any],
    agents_activated: dict[str, list[str]],
    runtime_ms: int,
    risk_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "router_decision": router_decision,
        "agents_activated": agents_activated,
        "latency": {"runtime_ms": runtime_ms},
        "risk_result": risk_result,
    }
