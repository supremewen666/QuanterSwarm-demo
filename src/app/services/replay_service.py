"""Replay service for stored run artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.common import DEFAULT_CAPITAL, ensure_directory, utc_now_iso
from app.services.portfolio_service import mock_execution_from_report, portfolio_plan_from_report
from quanter_swarm.backtest.replay_engine import replay_report
from quanter_swarm.core.runtime.config import load_settings
from quanter_swarm.core.storage.file_store import write_json
from quanter_swarm.errors import BacktestError


def _resolve_report_path(run_id: str) -> Path:
    settings = load_settings()
    reports_dir = settings.data_dir / "reports"
    candidates = sorted(reports_dir.glob(f"*{run_id}*.json"))
    if not candidates:
        raise BacktestError(f"Unable to locate report artifact for run_id '{run_id}'.")
    return candidates[-1]


def run_replay(*, run_id: str, capital: float = DEFAULT_CAPITAL) -> dict[str, Any]:
    report_path = _resolve_report_path(run_id)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    replay = replay_report(report, capital)
    payload: dict[str, Any] = {
        "run_id": run_id,
        "replayed_at": utc_now_iso(),
        "report_path": str(report_path),
        "symbol": report.get("symbol"),
        "experiment_id": report.get("decision_trace_summary", {}).get("trace_id"),
        "dataset_version": f"report:{report.get('symbol', 'unknown').lower()}",
        "config_hash": report.get("config_provenance", {}).get("fingerprint", "unknown"),
        "router_version": f"router:{report.get('config_provenance', {}).get('fingerprint', 'unknown')[:8]}",
        "ranking_version": f"ranking:{report.get('config_provenance', {}).get('fingerprint', 'unknown')[:8]}",
        "risk_version": f"risk:{report.get('config_provenance', {}).get('fingerprint', 'unknown')[:8]}",
        "portfolio_plan": portfolio_plan_from_report(report),
        "execution_report": mock_execution_from_report(report),
        "replay": replay,
    }
    settings = load_settings()
    replay_dir = ensure_directory(settings.data_dir / "replays")
    write_json(replay_dir / f"{run_id}.json", payload)
    write_json(replay_dir / "latest.json", payload)
    return payload
