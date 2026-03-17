"""Event models for backtest and replay flows."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class BacktestEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: str
    symbol: str
    trace_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class MarketEvent(BacktestEvent):
    event_type: Literal["market"] = "market"


class SignalEvent(BacktestEvent):
    event_type: Literal["signal"] = "signal"


class OrderEvent(BacktestEvent):
    event_type: Literal["order"] = "order"


class FillEvent(BacktestEvent):
    event_type: Literal["fill"] = "fill"


class PortfolioUpdateEvent(BacktestEvent):
    event_type: Literal["portfolio_update"] = "portfolio_update"
