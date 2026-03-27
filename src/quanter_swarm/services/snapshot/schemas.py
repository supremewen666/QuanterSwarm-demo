"""Typed schema helpers for point-in-time data records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any


def iso_to_epoch(value: str | int | float | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    normalized = value.replace("Z", "+00:00")
    return int(datetime.fromisoformat(normalized).timestamp())


def _to_iso(value: str | int | float | None, fallback_ts: int) -> str:
    if value is None:
        return datetime.fromtimestamp(fallback_ts, tz=UTC).isoformat()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(int(value), tz=UTC).isoformat()
    return value.replace("Z", "+00:00")


def record_hash(payload: dict[str, Any]) -> str:
    return sha256(repr(sorted(payload.items())).encode("utf-8")).hexdigest()


@dataclass(slots=True)
class RecordMetadata:
    as_of_ts: int
    available_at: str
    ingested_at: str
    source: str
    source_type: str
    record_id: str
    schema_version: str = "2026-03-18"
    quality_flags: list[str] = field(default_factory=list)
    reliability_score: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "as_of_ts": self.as_of_ts,
            "available_at": self.available_at,
            "ingested_at": self.ingested_at,
            "source": self.source,
            "source_type": self.source_type,
            "record_id": self.record_id,
            "schema_version": self.schema_version,
            "quality_flags": list(self.quality_flags),
            "reliability_score": round(float(self.reliability_score), 4),
        }


def make_metadata(
    *,
    as_of_ts: int,
    source: str,
    source_type: str,
    record_key: str,
    available_at: str | int | float | None = None,
    ingested_at: str | int | float | None = None,
    quality_flags: list[str] | None = None,
    reliability_score: float = 0.0,
) -> RecordMetadata:
    return RecordMetadata(
        as_of_ts=as_of_ts,
        available_at=_to_iso(available_at, as_of_ts),
        ingested_at=_to_iso(ingested_at, as_of_ts),
        source=source,
        source_type=source_type,
        record_id=record_hash({"record_key": record_key, "source": source, "as_of_ts": as_of_ts}),
        quality_flags=list(quality_flags or []),
        reliability_score=reliability_score,
    )
