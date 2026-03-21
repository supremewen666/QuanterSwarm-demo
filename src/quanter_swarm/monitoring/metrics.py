"""Runtime-facing monitoring metrics."""

from __future__ import annotations

from typing import Any


def build_runtime_monitoring_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    trace_summary = report.get("decision_trace_summary", {})
    metrics = trace_summary.get("metrics", {})
    routing = report.get("router_decision", {})
    risk = report.get("risk_check", {})
    token_cost = metrics.get("token_cost", {})
    return {
        "latency": {
            "runtime_ms": trace_summary.get("runtime_ms", 0),
            "routing_ms": metrics.get("router_latency", {}).get("routing_ms", 0),
            "agent_execution_ms": metrics.get("agent_latency", {}).get("agent_execution_ms", 0),
        },
        "token_usage": {
            "estimated_tokens": token_cost.get("estimated_tokens", 0),
            "budget": token_cost.get("budget", "unknown"),
        },
        "routing_decisions": {
            "regime": routing.get("regime"),
            "leaders": routing.get("leader_selected", []),
            "specialists": routing.get("specialists_selected", []),
            "confidence": routing.get("confidence", 0.0),
        },
        "risk_triggers": {
            "status": risk.get("status"),
            "reason": risk.get("reason"),
            "warnings": risk.get("warnings", []),
        },
    }
