"""Low-level helpers for temporal data integrity checks."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from quanter_swarm.errors import DataProviderError


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=UTC)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise DataProviderError(f"Invalid timestamp '{value}'.") from exc
    raise DataProviderError("Timestamp value is missing.")


def ensure_not_future(value: Any, *, upper_bound: datetime, field_name: str, grace_seconds: float = 1.0) -> None:
    timestamp = parse_timestamp(value)
    if timestamp.timestamp() - upper_bound.timestamp() > grace_seconds:
        raise DataProviderError(f"{field_name} uses future data: {timestamp.isoformat()} > {upper_bound.isoformat()}")


def ensure_monotonic(
    older: Any,
    newer: Any,
    *,
    older_name: str,
    newer_name: str,
    grace_seconds: float = 1.0,
) -> None:
    older_ts = parse_timestamp(older)
    newer_ts = parse_timestamp(newer)
    if older_ts.timestamp() - newer_ts.timestamp() > grace_seconds:
        raise DataProviderError(f"{older_name} must be <= {newer_name}.")
