import json
from pathlib import Path

from quanter_swarm.agents.specialists import DataFetchSpecialist
from quanter_swarm.services.data.mock_provider import MockDataProvider
from quanter_swarm.services.snapshot.cache import FileSnapshotCache, MemorySnapshotCache


def test_memory_snapshot_cache_round_trips_snapshot() -> None:
    cache = MemorySnapshotCache()
    cache.set_snapshot("AAPL", {"symbol": "AAPL", "snapshot_hash": "abc"})
    assert cache.get_snapshot("AAPL") == {"symbol": "AAPL", "snapshot_hash": "abc"}


def test_file_snapshot_cache_persists_snapshot(tmp_path: Path) -> None:
    cache = FileSnapshotCache(tmp_path)
    cache.set_snapshot("MSFT", {"symbol": "MSFT", "snapshot_hash": "xyz"})
    assert json.loads((tmp_path / "msft.json").read_text(encoding="utf-8"))["symbol"] == "MSFT"
    assert cache.get_snapshot("MSFT") == {"symbol": "MSFT", "snapshot_hash": "xyz"}


def test_data_fetch_specialist_reads_from_cache_when_available() -> None:
    provider = MockDataProvider(
        latest_prices={"AAPL": {"symbol": "AAPL", "price": 101.5, "avg_volume": 1_000_000, "change_pct": 0.01, "volatility": 0.03, "closes": [99.0, 100.0, 101.0]}},
        price_history={"AAPL": [{"symbol": "AAPL", "close": 99.0}, {"symbol": "AAPL", "close": 100.0}, {"symbol": "AAPL", "close": 101.0}]},
        news={"AAPL": [{"symbol": "AAPL", "headline": "AAPL stable demand"}]},
    )
    cache = MemorySnapshotCache()
    specialist = DataFetchSpecialist(provider=provider, cache=cache)

    first = specialist.fetch("AAPL")
    second = specialist.fetch("AAPL")

    assert first["symbol"] == "AAPL"
    assert second["cache_hit"] is True
    assert second["snapshot_hash"] == first["snapshot_hash"]
