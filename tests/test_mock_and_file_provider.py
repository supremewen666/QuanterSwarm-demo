from pathlib import Path

import pandas as pd

from quanter_swarm.errors import DataProviderError
from quanter_swarm.services.data.file_provider import FileDataProvider
from quanter_swarm.services.data.mock_provider import MockDataProvider


def test_mock_data_provider_returns_seeded_payloads() -> None:
    provider = MockDataProvider(
        latest_prices={"AAPL": {"symbol": "AAPL", "price": 101.5}},
        price_history={"AAPL": [{"symbol": "AAPL", "close": 99.0}, {"symbol": "AAPL", "close": 100.0}]},
        news={"AAPL": [{"symbol": "AAPL", "headline": "AAPL stable demand"}]},
    )
    assert provider.get_latest_price("aapl")["price"] == 101.5
    assert provider.get_price_history("AAPL", lookback=1) == [{"symbol": "AAPL", "close": 100.0}]
    assert provider.get_news("AAPL")[0]["headline"] == "AAPL stable demand"
    assert provider.data_source == "mock"


def test_file_data_provider_reads_csv_inputs(tmp_path: Path) -> None:
    (tmp_path / "latest_price_AAPL.csv").write_text(
        "symbol,price,avg_volume,change_pct,volatility\nAAPL,101.2,1200000,0.01,0.03\n",
        encoding="utf-8",
    )
    (tmp_path / "price_history_AAPL.csv").write_text(
        "symbol,close\nAAPL,99.1\nAAPL,100.2\nAAPL,101.2\n",
        encoding="utf-8",
    )
    (tmp_path / "news_AAPL.csv").write_text(
        "symbol,headline\nAAPL,AAPL launches product refresh\nAAPL,AAPL stable enterprise demand\n",
        encoding="utf-8",
    )

    provider = FileDataProvider(tmp_path)
    assert provider.get_latest_price("aapl")["price"] == 101.2
    assert len(provider.get_price_history("AAPL", lookback=2)) == 2
    assert provider.get_news("AAPL", limit=1)[0]["headline"] == "AAPL launches product refresh"
    assert provider.data_source.startswith("file:")


def test_file_data_provider_reads_parquet_when_csv_missing(tmp_path: Path, monkeypatch) -> None:
    expected = pd.DataFrame([{"symbol": "MSFT", "headline": "MSFT cloud demand resilient"}])

    def _fake_read_parquet(path: Path) -> pd.DataFrame:
        assert path.name == "news_MSFT.parquet"
        return expected

    monkeypatch.setattr(pd, "read_parquet", _fake_read_parquet)
    (tmp_path / "news_MSFT.parquet").write_text("placeholder", encoding="utf-8")

    provider = FileDataProvider(tmp_path)
    assert provider.get_news("MSFT")[0]["headline"] == "MSFT cloud demand resilient"


def test_file_data_provider_raises_for_missing_dataset(tmp_path: Path) -> None:
    provider = FileDataProvider(tmp_path)
    try:
        provider.get_latest_price("NVDA")
    except DataProviderError as exc:
        assert "Missing latest_price data" in str(exc)
    else:
        raise AssertionError("Expected DataProviderError for missing file-backed data.")
