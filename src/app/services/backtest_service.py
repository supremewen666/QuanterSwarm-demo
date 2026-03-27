"""Backtest service backed by replayable cycle reports."""

from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.common import (
    ensure_directory,
    normalize_source,
    resolve_symbols,
    safe_fingerprint,
    utc_now_iso,
)
from app.services.portfolio_service import mock_execution_from_report, portfolio_plan_from_report
from app.services.research_cycle import run_research_cycle
from quanter_swarm.backtest.replay_engine import replay_report
from quanter_swarm.core.runtime.config import load_settings
from quanter_swarm.core.storage.file_store import write_json


def _metric_average(reports: list[dict[str, Any]], metric_name: str) -> float:
    values = [
        float(report.get("evaluation_summary", {}).get("metrics", {}).get(metric_name, 0.0))
        for report in reports
    ]
    if not values:
        return 0.0
    return round(mean(values), 6)


def run_backtest(
    *,
    source: str = "internal_sim",
    symbols: list[str] | None = None,
    config_path: str | None = None,
    capital: float = 100_000.0,
) -> dict[str, Any]:
    normalized_source = normalize_source(source)
    reports = run_research_cycle(source=normalized_source, symbols=resolve_symbols(symbols))
    replay_rows = [replay_report(report, capital) for report in reports]
    created_at = utc_now_iso()
    first_report = reports[0] if reports else {}
    config_hash = safe_fingerprint(first_report)
    run_id = created_at.replace(":", "").replace("-", "")
    payload = {
        "run_id": run_id,
        "created_at": created_at,
        "source": normalized_source,
        "symbols": [report.get("symbol") for report in reports],
        "dataset_version": f"{normalized_source}:{created_at[:10]}",
        "config_hash": config_hash,
        "router_version": f"router:{config_hash[:8]}",
        "ranking_version": f"ranking:{config_hash[:8]}",
        "risk_version": f"risk:{config_hash[:8]}",
        "config_path": config_path,
        "summary": {
            "return": _metric_average(reports, "annualized_return"),
            "sharpe": _metric_average(reports, "sharpe"),
            "drawdown": _metric_average(reports, "drawdown"),
            "turnover": _metric_average(reports, "turnover_proxy"),
            "realized_return": round(mean(row["realized_return"] for row in replay_rows), 6) if replay_rows else 0.0,
        },
        "results": [
            {
                "symbol": report.get("symbol"),
                "report": report,
                "replay": replay,
                "portfolio_plan": portfolio_plan_from_report(report),
                "execution_report": mock_execution_from_report(report),
            }
            for report, replay in zip(reports, replay_rows, strict=True)
        ],
    }
    settings = load_settings()
    backtests_dir = ensure_directory(settings.data_dir / "backtests")
    write_json(backtests_dir / f"{run_id}.json", payload)
    write_json(backtests_dir / "latest.json", payload)
    return payload
