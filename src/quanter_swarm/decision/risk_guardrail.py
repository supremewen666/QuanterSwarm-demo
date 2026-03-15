"""Risk guardrails."""

from __future__ import annotations


SEVERE_WARNINGS = {"elevated_macro_risk", "drawdown_breach", "panic_regime"}


def assess_guardrails(risk_report: dict) -> dict:
    warnings = list(risk_report.get("warnings", []))
    if not warnings:
        return {
            "status": "pass",
            "approved": True,
            "exposure_multiplier": 1.0,
            "reason": "approved",
            "warnings": warnings,
        }

    if any(warning in SEVERE_WARNINGS for warning in warnings) or len(warnings) >= 2:
        return {
            "status": "blocked",
            "approved": False,
            "exposure_multiplier": 0.0,
            "reason": "risk_rejected",
            "warnings": warnings,
        }

    return {
        "status": "reduced",
        "approved": True,
        "exposure_multiplier": 0.5,
        "reason": "reduced_exposure_required",
        "warnings": warnings,
    }


def passes_guardrails(risk_report: dict) -> bool:
    return assess_guardrails(risk_report)["status"] == "pass"
