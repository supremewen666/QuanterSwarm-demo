"""Schema-first contracts shared by API, CLI, orchestration, and reporting."""

from __future__ import annotations

from typing import Literal

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


class PortfolioPositionContract(BaseModel):
    symbol: str
    leader: str
    weight: float


class PortfolioSuggestionContract(BaseModel):
    model_config = ConfigDict(extra="allow")
    positions: list[PortfolioPositionContract]
    cash_buffer: float
    gross_exposure: float
    mode: str
    allocation_mode: str
    rationale: str


class PaperTradeActionContract(BaseModel):
    model_config = ConfigDict(extra="allow")
    executed: bool
    status: str
    order_id: str
    decision_price: float
    fill_price: float
    total_cost: float
    order: dict


class FinalReportContract(BaseModel):
    model_config = ConfigDict(extra="allow")
    symbol: str
    active_regime: str
    regime_confidence: float
    active_strategy_teams: list[str]
    market_summary: dict
    fundamentals_summary: dict
    sentiment_summary: dict
    event_impact_summary: dict
    factor_scorecard: dict
    risk_alerts: dict
    portfolio_suggestion: PortfolioSuggestionContract
    paper_trade_actions: list[PaperTradeActionContract]
    evaluation_summary: dict
    one_page_summary: dict
    decision_trace: dict | None = None
    decision_trace_summary: dict
