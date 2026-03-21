"""Schemas for tool invocation and output."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from quanter_swarm.contracts import Status


class ToolExecutionResult(BaseModel):
    tool_name: str
    status: Status = Status.OK
    reason: str = ""
    fallback_flags: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    payload: dict[str, Any] = Field(default_factory=dict)
    attempts: int = 1
    duration_ms: int = 0
    error_type: str | None = None
