"""API schemas."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    status: str


class ResearchRequest(BaseModel):
    symbol: str | None = Field(default=None, min_length=1, max_length=12)
    symbols: list[str] | None = Field(default=None, min_length=1, max_length=20)
    horizon: Literal["1d", "1w", "2w", "1m"] = "1w"
    portfolio_mode: Literal["single", "multi"] = "single"
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    output_format: Literal["json", "markdown"] = "json"
    data_freshness_preference: Literal["latest", "cached"] = "latest"

    @model_validator(mode="after")
    def _validate_symbol_payload(self) -> "ResearchRequest":
        if not self.symbol and not self.symbols:
            raise ValueError("Either symbol or symbols must be provided.")
        return self


class ResearchResponse(BaseModel):
    symbol: str
    regime: str
    active_regime: str
    regime_confidence: float
    active_strategy_teams: list[str]
    market_summary: dict
    fundamentals_summary: dict
    sentiment_summary: dict
    event_impact_summary: dict
    factor_scorecard: dict
    risk_alerts: dict
    portfolio_suggestion: dict
    paper_trade_actions: list[dict]
    evaluation_summary: dict
    one_page_summary: dict
    decision_trace_summary: dict


class BatchResearchResponse(BaseModel):
    results: list[ResearchResponse]
