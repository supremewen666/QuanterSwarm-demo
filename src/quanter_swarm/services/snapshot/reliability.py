"""Source reliability scoring and cross-source consistency helpers."""

from __future__ import annotations

from typing import Any

from quanter_swarm.services.snapshot.schemas import iso_to_epoch

_AUTHORITY_BY_SOURCE_TYPE = {
    "official": 0.98,
    "exchange": 0.97,
    "commercial": 0.9,
    "file": 0.84,
    "derived": 0.76,
    "synthetic": 0.7,
    "mock": 0.62,
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _timeliness_score(record: dict[str, Any]) -> float:
    as_of_ts = int(record.get("as_of_ts", 0) or 0)
    available_ts = iso_to_epoch(record.get("available_at"))
    if not as_of_ts or available_ts is None:
        return 0.0
    if available_ts <= as_of_ts:
        lag = as_of_ts - available_ts
        return _clamp(1.0 - min(0.6, lag / 86_400))
    return 0.0


def _consistency_score(record: dict[str, Any]) -> float:
    if "cross_source_confirmed" in record.get("quality_flags", []):
        return 0.98
    if "restated" in record.get("quality_flags", []):
        return 0.55
    if "missing_available_at" in record.get("quality_flags", []):
        return 0.35
    return 0.82


def compute_source_reliability(record: dict[str, Any]) -> dict[str, Any]:
    source_type = str(record.get("source_type", "derived"))
    authority_score = _AUTHORITY_BY_SOURCE_TYPE.get(source_type, 0.72)
    timeliness_score = _timeliness_score(record)
    completeness_score = 1.0 if record.get("record_id") and record.get("source") else 0.7
    consistency_score = _consistency_score(record)
    revision_stability = 0.55 if "restated" in record.get("quality_flags", []) else 0.9
    mapping_confidence = 0.75 if "mapping_low_confidence" in record.get("quality_flags", []) else 0.95
    reliability_score = _clamp(
        authority_score * 0.3
        + timeliness_score * 0.2
        + completeness_score * 0.15
        + consistency_score * 0.15
        + revision_stability * 0.1
        + mapping_confidence * 0.1
    )
    return {
        "reliability_score": round(reliability_score, 4),
        "authority_score": round(authority_score, 4),
        "timeliness_score": round(timeliness_score, 4),
        "consistency_score": round(consistency_score, 4),
        "quality_flags": list(record.get("quality_flags", [])),
    }


def consistency_check(records: list[dict[str, Any]], field: str, tolerance: float = 0.02) -> dict[str, Any]:
    observed = [float(record[field]) for record in records if record.get(field) is not None]
    if len(observed) <= 1:
        return {"consistent": True, "spread": 0.0}
    spread = max(observed) - min(observed)
    return {"consistent": spread <= tolerance, "spread": round(spread, 6)}
