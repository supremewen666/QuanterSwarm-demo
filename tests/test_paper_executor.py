from quanter_swarm.execution.paper_executor import execute


def test_paper_executor_handles_event_window_with_delayed_fill() -> None:
    result = execute(
        {
            "symbol": "NVDA",
            "leader": "breakout_event",
            "notional": 120_000,
            "reference_price": 100,
            "decision_price": 100,
            "volatility": 0.09,
            "avg_volume": 300_000,
            "gap_pct": 0.03,
            "is_open_session": True,
            "event_window": True,
        }
    )
    assert result["status"] in {"delayed", "unfilled", "partial", "accepted"}
    assert result["fill_price"] >= result["decision_price"]
