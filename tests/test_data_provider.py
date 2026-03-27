from quanter_swarm.agents.specialists.data_fetch_specialist import DataFetchSpecialist
from quanter_swarm.services.data.base import (
    BaseDataProvider,
    DeterministicDataProvider,
    get_default_data_provider,
)
from quanter_swarm.services.snapshot.reliability import compute_source_reliability


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
    assert snapshot["available_at"]
    assert snapshot["reliability_score"] > 0
    assert snapshot["market_packet"]["available_at"]
    assert snapshot["fundamentals_packet"]["available_at"]
    assert snapshot["macro_inputs"]["available_at"]
    assert snapshot["evidence"]["market"]["reliability_score"] > 0


def test_data_fetch_specialist_fetch_many_uses_batch_contract() -> None:
    specialist = DataFetchSpecialist(provider=DeterministicDataProvider())
    snapshots = specialist.fetch_many(["AAPL", "MSFT"])
    assert set(snapshots) == {"AAPL", "MSFT"}
    assert all(payload["market_packet"]["symbol"] in {"AAPL", "MSFT"} for payload in snapshots.values())
    assert all("shares_float_packet" in payload for payload in snapshots.values())


def test_compute_source_reliability_returns_breakdown() -> None:
    result = compute_source_reliability(
        {
            "as_of_ts": 1_773_000_000,
            "available_at": "2026-03-16T12:30:00+00:00",
            "source": "deterministic_macro",
            "source_type": "official",
            "record_id": "macro-1",
            "quality_flags": ["xbrl_normalized"],
        }
    )
    assert result["reliability_score"] > 0.5
    assert result["authority_score"] >= result["consistency_score"] - 0.2
