"""API schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ResearchRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=12)


class ResearchResponse(BaseModel):
    active_regime: str
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
