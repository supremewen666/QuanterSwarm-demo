"""Skill-facing request/response adapter."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from quanter_swarm.contracts import ResearchRequestContract
from quanter_swarm.orchestrator.root_agent import RootAgent

SkillMode = Literal["normal", "degraded", "missing_data", "no_trade"]


class SkillResponse(BaseModel):
    symbol: str
    regime: str
    regime_confidence: float
    active_leaders: list[str]
    thesis_summary: list[str]
    factor_scorecard: dict
    risk_alerts: dict
    portfolio_suggestion: dict
    paper_trade_actions: list[dict]
    evaluation_summary: dict
    decision_trace_summary: dict
    mode: SkillMode


def _scenario_from_mode(mode: SkillMode) -> dict[str, Any]:
    if mode == "degraded":
        return {"disable_specialists": {"sentiment": True, "macro_event": True}}
    if mode == "missing_data":
        return {"drop_news": True, "drop_fundamentals": True}
    if mode == "no_trade":
        return {"force_no_trade": True}
    return {}


def run_skill_request(request: dict[str, Any], mode: SkillMode = "normal") -> dict[str, Any]:
    parsed = ResearchRequestContract.model_validate(request)
    symbols = parsed.symbols or ([parsed.symbol] if parsed.symbol else [])
    symbol = symbols[0]
    report = RootAgent().run(symbol=symbol, scenario=_scenario_from_mode(mode))
    response = SkillResponse(
        symbol=report["symbol"],
        regime=report["active_regime"],
        regime_confidence=report["regime_confidence"],
        active_leaders=report["active_strategy_teams"],
        thesis_summary=report["one_page_summary"]["highlights"],
        factor_scorecard=report["factor_scorecard"],
        risk_alerts=report["risk_alerts"],
        portfolio_suggestion=report["portfolio_suggestion"],
        paper_trade_actions=report["paper_trade_actions"],
        evaluation_summary=report["evaluation_summary"],
        decision_trace_summary=report["decision_trace_summary"],
        mode=mode,
    )
    return response.model_dump()
