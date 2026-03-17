"""Backtest domain models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Order(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str
    leader: str | None = None
    notional: float
    reference_price: float | None = None
    decision_price: float | None = None


class Fill(BaseModel):
    model_config = ConfigDict(extra="allow")

    order_id: str
    status: str
    fill_price: float
    fill_ratio: float
    total_cost: float
    filled_notional: float | None = None


class Position(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str
    leader: str
    weight: float


class Portfolio(BaseModel):
    model_config = ConfigDict(extra="allow")

    positions: list[Position] = Field(default_factory=list)
    gross_exposure: float
    cash_buffer: float
    mode: str
    allocation_mode: str
