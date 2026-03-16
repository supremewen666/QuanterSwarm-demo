"""Leaderboard, monitoring, and drift detection helpers."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from time import time
from typing import Any

from pydantic import ValidationError

from quanter_swarm.contracts import FinalReportContract


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    idx = (len(ordered) - 1) * pct
    lower = int(idx)
    upper = min(lower + 1, len(ordered) - 1)
    weight = idx - lower
    return float(ordered[lower] * (1 - weight) + ordered[upper] * weight)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_reports(report_dir: Path | str) -> list[dict[str, Any]]:
    root = Path(report_dir)
    if not root.exists():
        return []
    files = sorted(root.glob("*.json"), key=lambda item: item.stat().st_mtime)
    rows: list[dict[str, Any]] = []
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _leaderboard(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stats: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "activation_count": 0.0,
            "trade_count": 0.0,
            "rank_score_total": 0.0,
            "net_score_total": 0.0,
            "weight_total": 0.0,
            "win_count": 0.0,
        }
    )
    for report in reports:
        leaders = report.get("active_strategy_teams", [])
        if isinstance(leaders, list):
            for leader in leaders:
                stats[leader]["activation_count"] += 1

        for position in report.get("portfolio_suggestion", {}).get("positions", []):
            leader = position.get("leader")
            if not leader:
                continue
            stats[leader]["trade_count"] += 1
            stats[leader]["weight_total"] += _as_float(position.get("weight"))

        top_leader = report.get("evaluation_summary", {}).get("top_signal", {}).get("leader")
        if top_leader:
            stats[top_leader]["win_count"] += 1

        for row in report.get("decision_trace_summary", {}).get("leader_scores", []):
            leader = row.get("leader")
            if not leader:
                continue
            rank_score = _as_float(row.get("rank_score"))
            risk_penalty = _as_float(row.get("risk_penalty"))
            stats[leader]["rank_score_total"] += rank_score
            stats[leader]["net_score_total"] += rank_score - risk_penalty

    leaderboard = []
    for leader, row in stats.items():
        activation_count = int(row["activation_count"])
        trade_count = int(row["trade_count"])
        leaderboard.append(
            {
                "leader": leader,
                "activation_count": activation_count,
                "trade_count": trade_count,
                "avg_rank_score": round(row["rank_score_total"] / max(1, activation_count), 4),
                "avg_net_score": round(row["net_score_total"] / max(1, activation_count), 4),
                "avg_weight": round(row["weight_total"] / max(1, trade_count), 4),
                "win_rate_proxy": round(row["win_count"] / max(1, activation_count), 4),
            }
        )
    return sorted(leaderboard, key=lambda item: (item["avg_net_score"], item["activation_count"]), reverse=True)


def _regime_breakdown(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "sharpe": [],
            "drawdown": [],
            "turnover": [],
            "gross_exposure": [],
            "cash_buffer": [],
            "no_trade_count": 0,
        }
    )
    for report in reports:
        regime = report.get("active_regime", "unknown")
        bucket = grouped[regime]
        bucket["count"] += 1
        metrics = report.get("evaluation_summary", {}).get("metrics", {})
        bucket["sharpe"].append(_as_float(metrics.get("sharpe")))
        bucket["drawdown"].append(_as_float(metrics.get("drawdown")))
        bucket["turnover"].append(_as_float(metrics.get("turnover_proxy")))
        portfolio = report.get("portfolio_suggestion", {})
        bucket["gross_exposure"].append(_as_float(portfolio.get("gross_exposure")))
        bucket["cash_buffer"].append(_as_float(portfolio.get("cash_buffer"), 1.0))
        if portfolio.get("mode") == "no_trade":
            bucket["no_trade_count"] += 1

    rows = []
    for regime, bucket in grouped.items():
        count = max(1, int(bucket["count"]))
        rows.append(
            {
                "regime": regime,
                "count": int(bucket["count"]),
                "avg_sharpe": round(_mean(bucket["sharpe"]), 4),
                "avg_drawdown": round(_mean(bucket["drawdown"]), 4),
                "avg_turnover": round(_mean(bucket["turnover"]), 4),
                "avg_gross_exposure": round(_mean(bucket["gross_exposure"]), 4),
                "avg_cash_buffer": round(_mean(bucket["cash_buffer"]), 4),
                "no_trade_rate": round(bucket["no_trade_count"] / count, 4),
            }
        )
    return sorted(rows, key=lambda item: item["count"], reverse=True)


def _quality_snapshot(reports: list[dict[str, Any]]) -> dict[str, Any]:
    score_fields = [
        lambda payload: bool(payload.get("symbol")),
        lambda payload: bool(payload.get("active_regime")),
        lambda payload: isinstance(payload.get("active_strategy_teams"), list),
        lambda payload: bool(payload.get("portfolio_suggestion", {}).get("mode")),
        lambda payload: bool(payload.get("evaluation_summary", {}).get("metrics")),
        lambda payload: isinstance(payload.get("decision_trace_summary", {}).get("routing"), dict),
        lambda payload: isinstance(payload.get("decision_trace_summary", {}).get("state_machine", {}).get("stages"), list),
    ]
    schema_invalid_count = 0
    scores: list[float] = []
    for report in reports:
        passed = sum(1 for check in score_fields if check(report))
        scores.append(passed / len(score_fields))
        try:
            FinalReportContract.model_validate(report)
        except ValidationError:
            schema_invalid_count += 1
    return {
        "avg_completeness": round(_mean(scores), 4),
        "min_completeness": round(min(scores), 4) if scores else 0.0,
        "schema_invalid_count": schema_invalid_count,
        "sample_count": len(reports),
    }


def _latency_snapshot(reports: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [
        _as_float(report.get("decision_trace_summary", {}).get("runtime_ms"))
        for report in reports
        if report.get("decision_trace_summary", {}).get("runtime_ms") is not None
    ]
    if not latencies:
        return {
            "sample_count": 0,
            "avg_runtime_ms": 0.0,
            "p50_runtime_ms": 0.0,
            "p90_runtime_ms": 0.0,
            "p95_runtime_ms": 0.0,
            "max_runtime_ms": 0.0,
        }
    return {
        "sample_count": len(latencies),
        "avg_runtime_ms": round(_mean(latencies), 2),
        "p50_runtime_ms": round(_percentile(latencies, 0.5), 2),
        "p90_runtime_ms": round(_percentile(latencies, 0.9), 2),
        "p95_runtime_ms": round(_percentile(latencies, 0.95), 2),
        "max_runtime_ms": round(max(latencies), 2),
    }


def _distribution(values: list[str]) -> dict[str, float]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    total = max(1, sum(counts.values()))
    return {key: counts[key] / total for key in sorted(counts)}


def _drift_snapshot(reports: list[dict[str, Any]], baseline_window: int, recent_window: int) -> dict[str, Any]:
    required = baseline_window + recent_window
    if len(reports) < required:
        return {
            "status": "insufficient_data",
            "alerts": [],
            "required_reports": required,
            "available_reports": len(reports),
        }

    baseline = reports[-required:-recent_window]
    recent = reports[-recent_window:]
    alerts: list[dict[str, Any]] = []

    baseline_regime = _distribution([item.get("active_regime", "unknown") for item in baseline])
    recent_regime = _distribution([item.get("active_regime", "unknown") for item in recent])
    regime_shift = {
        regime: round(abs(recent_regime.get(regime, 0.0) - baseline_regime.get(regime, 0.0)), 4)
        for regime in set(baseline_regime) | set(recent_regime)
    }
    significant_regime = {k: v for k, v in regime_shift.items() if v >= 0.35}
    if significant_regime:
        alerts.append({"type": "regime_distribution_shift", "details": significant_regime})

    baseline_leaders = _distribution([leader for item in baseline for leader in item.get("active_strategy_teams", [])])
    recent_leaders = _distribution([leader for item in recent for leader in item.get("active_strategy_teams", [])])
    leader_shift = {
        leader: round(abs(recent_leaders.get(leader, 0.0) - baseline_leaders.get(leader, 0.0)), 4)
        for leader in set(baseline_leaders) | set(recent_leaders)
    }
    significant_leader = {k: v for k, v in leader_shift.items() if v >= 0.3}
    if significant_leader:
        alerts.append({"type": "leader_activation_shift", "details": significant_leader})

    baseline_sharpe = _mean([_as_float(item.get("evaluation_summary", {}).get("metrics", {}).get("sharpe")) for item in baseline])
    recent_sharpe = _mean([_as_float(item.get("evaluation_summary", {}).get("metrics", {}).get("sharpe")) for item in recent])
    sharpe_delta = round(recent_sharpe - baseline_sharpe, 4)
    if sharpe_delta <= -0.5:
        alerts.append({"type": "sharpe_drift", "details": {"delta": sharpe_delta}})

    baseline_quality = _quality_snapshot(baseline)["avg_completeness"]
    recent_quality = _quality_snapshot(recent)["avg_completeness"]
    quality_delta = round(recent_quality - baseline_quality, 4)
    if quality_delta <= -0.15:
        alerts.append({"type": "output_quality_drop", "details": {"delta": quality_delta}})

    baseline_latency = _latency_snapshot(baseline)["avg_runtime_ms"]
    recent_latency = _latency_snapshot(recent)["avg_runtime_ms"]
    if baseline_latency > 0:
        latency_ratio = round(recent_latency / baseline_latency, 4)
        if latency_ratio >= 1.5 and (recent_latency - baseline_latency) >= 50:
            alerts.append(
                {
                    "type": "latency_regression",
                    "details": {
                        "baseline_runtime_ms": baseline_latency,
                        "recent_runtime_ms": recent_latency,
                        "ratio": latency_ratio,
                    },
                }
            )

    return {
        "status": "alert" if alerts else "stable",
        "alerts": alerts,
        "baseline_window": baseline_window,
        "recent_window": recent_window,
    }


def build_monitoring_snapshot(
    reports: list[dict[str, Any]],
    baseline_window: int = 20,
    recent_window: int = 10,
) -> dict[str, Any]:
    return {
        "generated_at": int(time()),
        "report_count": len(reports),
        "leaderboard": _leaderboard(reports),
        "regime_breakdown": _regime_breakdown(reports),
        "latency": _latency_snapshot(reports),
        "output_quality": _quality_snapshot(reports),
        "drift": _drift_snapshot(reports, baseline_window=baseline_window, recent_window=recent_window),
    }


def build_monitoring_from_report_dir(
    report_dir: Path | str,
    baseline_window: int = 20,
    recent_window: int = 10,
) -> dict[str, Any]:
    reports = load_reports(report_dir)
    return build_monitoring_snapshot(reports, baseline_window=baseline_window, recent_window=recent_window)
