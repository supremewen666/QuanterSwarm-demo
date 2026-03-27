"""Runtime-oriented monitoring extracts for a single cycle report."""

from __future__ import annotations

from typing import Any


def build_runtime_monitoring_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    trace_summary = report.get("decision_trace_summary", {})
    metrics = trace_summary.get("metrics", {})
    token_usage = metrics.get("token_cost", {})
    router_decision = report.get("router_decision", {})

    return {
        "symbol": report.get("symbol"),
        "regime": report.get("active_regime"),
        "latency": {
            "runtime_ms": trace_summary.get("runtime_ms", 0),
            **metrics.get("agent_latency", {}),
            **metrics.get("router_latency", {}),
        },
        "token_usage": token_usage,
        "routing_decisions": {
            "leaders": router_decision.get("leader_selected", []),
            "specialists": router_decision.get("specialists_selected", []),
            "rejected_candidates": router_decision.get("rejected_candidates", {}),
        },
        "risk": report.get("risk_check", {}),
        "portfolio": report.get("portfolio_suggestion", {}),
    }
