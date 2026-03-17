"""File-backed data provider for CSV and parquet snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from quanter_swarm.data.base import BaseDataProvider
from quanter_swarm.errors import DataProviderError


class FileDataProvider(BaseDataProvider):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.data_source = f"file:{self.root}"

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        frame = self._load_frame("price_history", symbol)
        rows = frame.tail(lookback).to_dict(orient="records")
        return [self._normalize_record(symbol, row) for row in rows]

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        frame = self._load_frame("latest_price", symbol)
        rows = frame.tail(1).to_dict(orient="records")
        if not rows:
            raise DataProviderError(f"No latest price rows found for {symbol.upper()}.")
        return self._normalize_record(symbol, rows[0])

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        frame = self._load_frame("news", symbol)
        rows = frame.head(limit).to_dict(orient="records")
        return [self._normalize_record(symbol, row) for row in rows]

    def _load_frame(self, dataset: str, symbol: str) -> pd.DataFrame:
        symbol_upper = symbol.upper()
        csv_path = self.root / f"{dataset}_{symbol_upper}.csv"
        parquet_path = self.root / f"{dataset}_{symbol_upper}.parquet"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        if parquet_path.exists():
            return pd.read_parquet(parquet_path)
        raise DataProviderError(
            f"Missing {dataset} data for {symbol_upper} under {self.root}."
        )

    @staticmethod
    def _normalize_record(symbol: str, record: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(record)
        normalized.setdefault("symbol", symbol.upper())
        return normalized
