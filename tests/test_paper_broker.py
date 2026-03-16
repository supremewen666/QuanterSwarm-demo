from quanter_swarm.decision.paper_broker import PaperBroker


def test_paper_broker_accepts_order() -> None:
    result = PaperBroker().submit(
        {
            "symbol": "NVDA",
            "reference_price": 100,
            "decision_price": 100,
            "notional": 10000,
            "volatility": 0.03,
            "avg_volume": 1_000_000,
            "is_open_session": True,
            "gap_pct": 0.01,
        }
    )
    assert result["status"] in {"accepted", "partial", "delayed", "unfilled"}
    assert result["fill_price"] >= result["decision_price"]
    assert result["fill_ratio"] <= 1.0
    assert "audit" in result
