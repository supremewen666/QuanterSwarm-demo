from quanter_swarm.data.base import (
    BaseDataProvider,
    DeterministicDataProvider,
    get_default_data_provider,
)
from quanter_swarm.specialists.data_fetch_specialist import DataFetchSpecialist


def test_default_data_provider_implements_interface() -> None:
    provider = get_default_data_provider()
    assert isinstance(provider, BaseDataProvider)
    latest = provider.get_latest_price("AAPL")
    history = provider.get_price_history("AAPL", lookback=3)
    news = provider.get_news("AAPL", limit=2)
    assert latest["symbol"] == "AAPL"
    assert len(history) == 3
    assert all("close" in row for row in history)
    assert len(news) == 2


def test_data_fetch_specialist_uses_provider_contract() -> None:
    specialist = DataFetchSpecialist(provider=DeterministicDataProvider())
    snapshot = specialist.fetch("MSFT")
    assert snapshot["symbol"] == "MSFT"
    assert len(snapshot["market_packet"]["closes"]) == 5
    assert snapshot["news_inputs"]
    assert snapshot["data_source"] == "deterministic_local"
    assert snapshot["timestamp"].endswith("+00:00")
    assert len(snapshot["snapshot_hash"]) == 64
