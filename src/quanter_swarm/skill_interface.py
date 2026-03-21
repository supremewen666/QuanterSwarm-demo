"""Skill-facing request/response adapter."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from quanter_swarm.config.settings import Settings
from quanter_swarm.contracts import CycleReport, ResearchRequestContract
from quanter_swarm.orchestrator.root_agent import RootAgent
from quanter_swarm.orchestrator.runtime import RuntimeContext
from quanter_swarm.utils.config import load_settings

SkillMode = Literal["normal", "degraded", "missing_data", "no_trade"]


class SkillPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed_tools: list[str] = Field(default_factory=list)
    llm_provider_override: str | None = None
    llm_model_override: str | None = None
    tool_timeout: int | None = None
    strict_output: bool = True


class SkillResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
        return {"force_no_trade": True, "daily_loss_pct": 0.05}
    return {}


def _settings_with_policy(base: Settings, policy: SkillPolicy | None) -> Settings:
    if policy is None:
        return base
    return Settings(
        environment=base.environment,
        execution_mode=base.execution_mode,
        data_dir=base.data_dir,
        config_dir=base.config_dir,
        default_symbols=list(base.default_symbols),
        starting_capital=base.starting_capital,
        token_budget=base.token_budget,
        max_specialists_per_cycle=base.max_specialists_per_cycle,
        risk_thresholds=dict(base.risk_thresholds),
        backtest_window=dict(base.backtest_window),
        data_provider=dict(base.data_provider),
        llm_provider=policy.llm_provider_override or base.llm_provider,
        llm_model=policy.llm_model_override or base.llm_model,
        llm_temperature=base.llm_temperature,
        tool_timeout=policy.tool_timeout if policy.tool_timeout is not None else base.tool_timeout,
        tool_budget=base.tool_budget,
        allowed_tools=list(policy.allowed_tools or base.allowed_tools),
    )


def run_skill(
    request: ResearchRequestContract,
    *,
    mode: SkillMode = "normal",
    policy: SkillPolicy | None = None,
) -> CycleReport:
    symbols = request.symbols or ([request.symbol] if request.symbol else [])
    symbol = symbols[0]
    settings = _settings_with_policy(load_settings(), policy)
    runtime = RuntimeContext.build(settings=settings)
    report = RootAgent(runtime=runtime).run_sync(symbol=symbol, scenario=_scenario_from_mode(mode))
    validated = CycleReport.model_validate(report)
    if policy is not None and not policy.strict_output:
        return validated
    return CycleReport.model_validate(validated.model_dump())


def run_skill_request(
    request: dict[str, Any],
    mode: SkillMode = "normal",
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    parsed = ResearchRequestContract.model_validate(request)
    skill_policy = SkillPolicy.model_validate(policy or {})
    report = run_skill(parsed, mode=mode, policy=skill_policy)
    response = SkillResponse(
        symbol=report.symbol,
        regime=report.active_regime,
        regime_confidence=report.regime_confidence,
        active_leaders=report.active_strategy_teams,
        thesis_summary=list(report.one_page_summary.get("highlights", [])),
        factor_scorecard=report.factor_scorecard,
        risk_alerts=report.risk_alerts,
        portfolio_suggestion=report.portfolio_suggestion.model_dump(),
        paper_trade_actions=[item.model_dump() for item in report.paper_trade_actions],
        evaluation_summary=report.evaluation_summary,
        decision_trace_summary=report.decision_trace_summary,
        mode=mode,
    )
    return response.model_dump()
