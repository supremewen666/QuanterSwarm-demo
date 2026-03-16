"""Tracing helpers."""

from __future__ import annotations

from uuid import uuid4


def new_trace_id(prefix: str = "trace") -> str:
    return f"{prefix}_{uuid4().hex}"
