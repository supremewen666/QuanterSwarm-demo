"""Schema-first contracts shared by API, CLI, orchestration, and reporting."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ResearchRequestContract(BaseModel):
    symbol: str | None = Field(default=None, min_length=1, max_length=12)
    symbols: list[str] | None = Field(default=None, min_length=1, max_length=20)
    horizon: Literal["1d", "1w", "2w", "1m"] = "1w"
    portfolio_mode: Literal["single", "multi"] = "single"
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    output_format: Literal["json", "markdown"] = "json"
    data_freshness_preference: Literal["latest", "cached"] = "latest"

    @model_validator(mode="after")
    def _validate_symbol_payload(self) -> ResearchRequestContract:
        if not self.symbol and not self.symbols:
            raise ValueError("Either symbol or symbols must be provided.")
        return self


class AgentContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str
    regime: str | None = None
    market_summary: dict[str, Any] = Field(default_factory=dict)
    fundamentals_summary: dict[str, Any] = Field(default_factory=dict)
    sentiment_summary: dict[str, Any] = Field(default_factory=dict)
    event_impact_summary: dict[str, Any] = Field(default_factory=dict)
    features: dict[str, Any] = Field(default_factory=dict)
    scenario: dict[str, Any] = Field(default_factory=dict)
    compressed_context: str | None = None


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    agent_name: str
    role: str
    summary: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class LeaderOutputContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    leader: str
    symbol: str
    score: float
    thesis: str


class RankedIdeaContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    leader: str
    symbol: str
    score: float
    composite_rank_score: float
    confidence: float
    volatility: float
    correlation: float


class RouterDecision(BaseModel):
    model_config = ConfigDict(extra="allow")

    regime: str
    confidence: float
    leader_selected: list[str] = Field(default_factory=list)
    specialists_selected: list[str] = Field(default_factory=list)
    reasons: dict[str, str] = Field(default_factory=dict)
    rejected_candidates: dict[str, str] = Field(default_factory=dict)


class PortfolioPositionContract(BaseModel):
    symbol: str
    leader: str
    weight: float


class PortfolioSuggestion(BaseModel):
    model_config = ConfigDict(extra="allow")

    positions: list[PortfolioPositionContract]
    cash_buffer: float
    gross_exposure: float
    mode: str
    allocation_mode: str
    rationale: str
    no_trade_reason: str | None = None
    position_rationales: list[dict[str, Any]] = Field(default_factory=list)


class RiskCheckResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: str
    approved: bool
    exposure_multiplier: float
    reason: str
    warnings: list[str] = Field(default_factory=list)


class PaperTradeActionContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    executed: bool
    status: str
    order_id: str
    decision_price: float
    fill_price: float
    total_cost: float
    order: dict[str, Any]


class CycleReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str
    active_regime: str
    regime_confidence: float
    active_strategy_teams: list[str]
    market_summary: dict[str, Any]
    fundamentals_summary: dict[str, Any]
    sentiment_summary: dict[str, Any]
    event_impact_summary: dict[str, Any]
    factor_scorecard: dict[str, Any]
    risk_alerts: dict[str, Any]
    router_decision: RouterDecision
    risk_check: RiskCheckResult
    portfolio_suggestion: PortfolioSuggestion
    paper_trade_actions: list[PaperTradeActionContract]
    evaluation_summary: dict[str, Any]
    one_page_summary: dict[str, Any]
    config_provenance: dict[str, Any] = Field(default_factory=dict)
    decision_trace: dict[str, Any] | None = None
    decision_trace_summary: dict[str, Any]
    markdown_summary: str | None = None


PortfolioSuggestionContract = PortfolioSuggestion
FinalReportContract = CycleReport
