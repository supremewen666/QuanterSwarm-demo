"""Tracing helpers."""

from __future__ import annotations

from quanter_swarm.observability.trace import new_trace_id as _new_trace_id


def new_trace_id(prefix: str = "trace") -> str:
    return _new_trace_id(prefix)
