from quanter_swarm.market.data_quality import validate_snapshot


def test_validate_snapshot_flags_missing_news() -> None:
    summary = validate_snapshot(
        {
            "symbol": "AAPL",
            "as_of_ts": 1_773_000_000,
            "market_packet": {"price": 100},
            "fundamentals_packet": {"symbol": "AAPL"},
            "news_inputs": [],
        },
        staleness_sec=10_000_000,
    )
    assert "missing_news" in summary["issues"]


def test_validate_snapshot_flags_symbol_mismatch() -> None:
    summary = validate_snapshot(
        {
            "symbol": "AAPL",
            "as_of_ts": 1_773_000_000,
            "market_packet": {"price": 100},
            "fundamentals_packet": {"symbol": "MSFT"},
            "news_inputs": ["headline"],
        },
        staleness_sec=10_000_000,
    )
    assert "symbol_mismatch" in summary["issues"]
