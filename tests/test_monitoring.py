from __future__ import annotations

import json
from pathlib import Path

from quanter_swarm.evaluation.monitoring import (
    build_monitoring_from_report_dir,
    build_monitoring_snapshot,
)


def _report(
    idx: int,
    *,
    regime: str = "sideways",
    leaders: list[str] | None = None,
    sharpe: float = 0.5,
    drawdown: float = -0.1,
    turnover: float = 0.2,
    runtime_ms: int = 120,
    completeness_break: bool = False,
) -> dict:
    leaders = leaders or ["momentum"]
    payload = {
        "symbol": "AAPL",
        "active_regime": regime,
        "regime_confidence": 0.7,
        "active_strategy_teams": leaders,
        "market_summary": {"price": 100.0 + idx},
        "fundamentals_summary": {"quality_score": 0.6},
        "sentiment_summary": {"score": 0.55},
        "event_impact_summary": {"impact_score": 0.4},
        "factor_scorecard": {"score": 0.6},
        "risk_alerts": {"alerts": []},
        "portfolio_suggestion": {
            "positions": [{"symbol": "AAPL", "leader": leaders[0], "weight": 0.3}],
            "cash_buffer": 0.7,
            "gross_exposure": 0.3,
            "mode": "active",
            "allocation_mode": "volatility_aware",
            "rationale": "test",
        },
        "paper_trade_actions": [],
        "evaluation_summary": {
            "top_signal": {"leader": leaders[0]},
            "signal_count": 1,
            "metrics": {"sharpe": sharpe, "drawdown": drawdown, "turnover_proxy": turnover},
        },
        "one_page_summary": {"title": "test"},
        "decision_trace_summary": {
            "runtime_ms": runtime_ms,
            "routing": {"selected_reasons": {}, "skipped_reasons": {}},
            "state_machine": {"stages": [{"stage": "ingest", "status": "ok", "detail": {}}]},
            "leader_scores": [{"leader": leaders[0], "rank_score": 0.8, "risk_penalty": 0.1}],
        },
    }
    if completeness_break:
        payload.pop("decision_trace_summary")
    return payload


def test_monitoring_snapshot_includes_core_sections() -> None:
    snapshot = build_monitoring_snapshot(
        [
            _report(1, regime="sideways", leaders=["momentum"], sharpe=0.4),
            _report(2, regime="high_vol", leaders=["stat_arb"], sharpe=0.7, runtime_ms=260),
        ],
        baseline_window=1,
        recent_window=1,
    )
    assert snapshot["report_count"] == 2
    assert snapshot["leaderboard"][0]["leader"] in {"momentum", "stat_arb"}
    assert {row["regime"] for row in snapshot["regime_breakdown"]} == {"sideways", "high_vol"}
    assert snapshot["latency"]["p90_runtime_ms"] >= snapshot["latency"]["p50_runtime_ms"]
    assert snapshot["output_quality"]["avg_completeness"] > 0


def test_monitoring_from_dir_handles_invalid_and_legacy_reports(tmp_path: Path) -> None:
    (tmp_path / "ok.json").write_text(json.dumps(_report(1)), encoding="utf-8")
    (tmp_path / "legacy.json").write_text(json.dumps({"symbol": "AAPL", "active_regime": "sideways"}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{not-json", encoding="utf-8")
    snapshot = build_monitoring_from_report_dir(tmp_path, baseline_window=1, recent_window=1)
    assert snapshot["report_count"] == 2
    assert snapshot["output_quality"]["schema_invalid_count"] >= 1


def test_drift_detection_flags_regime_and_latency_shift() -> None:
    baseline = [
        _report(i, regime="sideways", leaders=["momentum"], sharpe=0.8, runtime_ms=100)
        for i in range(8)
    ]
    recent = [
        _report(100 + i, regime="risk_off", leaders=["stat_arb"], sharpe=-0.1, runtime_ms=260)
        for i in range(4)
    ]
    snapshot = build_monitoring_snapshot(baseline + recent, baseline_window=8, recent_window=4)
    drift_types = {item["type"] for item in snapshot["drift"]["alerts"]}
    assert snapshot["drift"]["status"] == "alert"
    assert "regime_distribution_shift" in drift_types
    assert "latency_regression" in drift_types


def test_output_quality_detects_missing_sections() -> None:
    snapshot = build_monitoring_snapshot([_report(1), _report(2, completeness_break=True)], baseline_window=1, recent_window=1)
    assert snapshot["output_quality"]["avg_completeness"] < 1.0
    assert snapshot["output_quality"]["schema_invalid_count"] >= 1
