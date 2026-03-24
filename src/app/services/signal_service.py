"""Signal generation service."""

from __future__ import annotations

from typing import Any

from app.services.common import ensure_directory, normalize_source, utc_now_iso
from app.services.research_cycle import run_research_cycle
from quanter_swarm.storage.file_store import write_json
from quanter_swarm.utils.config import load_settings


def _build_evidence_refs(report: dict[str, Any]) -> list[str]:
    sources = report.get("evidence_summary", {}).get("data_sources", {})
    refs: list[str] = []
    for name, payload in sources.items():
        if isinstance(payload, dict) and payload.get("available_at"):
            refs.append(f"{name}:{payload['available_at']}")
        elif isinstance(payload, list):
            refs.extend(
                f"{name}:{item.get('available_at', 'unknown')}"
                for item in payload
                if isinstance(item, dict)
            )
    return refs


def _build_agent_outputs(report: dict[str, Any]) -> dict[str, Any]:
    trace = report.get("decision_trace_summary", {})
    top_signal = report.get("evaluation_summary", {}).get("top_signal") or {}
    return {
        "leader": top_signal.get("leader"),
        "leader_scores": trace.get("leader_scores", []),
        "routing": trace.get("routing", {}),
        "specialist_contribution": trace.get("specialist_contribution", {}),
    }


def _signal_from_report(report: dict[str, Any], *, created_at: str) -> dict[str, Any]:
    top_signal = report.get("evaluation_summary", {}).get("top_signal") or {}
    rank_score = float(top_signal.get("composite_rank_score", 0.0))
    return {
        "signal_id": f"{report.get('symbol', 'unknown').lower()}-{created_at}",
        "symbol": report.get("symbol"),
        "direction": "long" if rank_score >= 0.5 else "flat",
        "confidence": float(top_signal.get("confidence", report.get("regime_confidence", 0.0))),
        "agent_outputs": _build_agent_outputs(report),
        "evidence_refs": _build_evidence_refs(report),
        "risk_flags": list(report.get("risk_alerts", {}).get("warnings", [])),
        "created_at": created_at,
        "score": rank_score,
        "portfolio_candidate": bool(report.get("portfolio_suggestion", {}).get("positions")),
        "regime": report.get("active_regime"),
    }


def generate_signals(
    *,
    source: str = "internal_sim",
    symbols: list[str] | None = None,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    normalized_source = normalize_source(source)
    reports = run_research_cycle(source=normalized_source, symbols=symbols)
    created_at = utc_now_iso()
    artifact_id = created_at.replace(":", "").replace("-", "")
    payload = {
        "artifact_id": artifact_id,
        "generated_at": created_at,
        "source": normalized_source,
        "as_of_date": as_of_date or created_at[:10],
        "signals": [_signal_from_report(report, created_at=created_at) for report in reports],
    }
    settings = load_settings()
    signals_dir = ensure_directory(settings.data_dir / "signals")
    write_json(signals_dir / f"signals_{artifact_id}.json", payload)
    write_json(signals_dir / "latest.json", payload)
    return payload
