"""Monitoring trace helpers."""

from __future__ import annotations

from typing import Any


def build_monitoring_trace(report: dict[str, Any]) -> dict[str, Any]:
    trace_summary = report.get("decision_trace_summary", {})
    trace = trace_summary.get("trace", {})
    return {
        "trace_id": trace_summary.get("trace_id", trace.get("trace_id")),
        "runtime_ms": trace_summary.get("runtime_ms", trace.get("latency", {}).get("runtime_ms", 0)),
        "router_decision": trace.get("router_decision", report.get("router_decision", {})),
        "risk_result": trace.get("risk_result", report.get("risk_check", {})),
        "metrics": trace.get("metrics", trace_summary.get("metrics", {})),
    }
