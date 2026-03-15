from quanter_swarm.decision.paper_broker import PaperBroker


def test_paper_broker_accepts_order() -> None:
    result = PaperBroker().submit({"symbol": "NVDA", "reference_price": 100})
    assert result["status"] == "accepted"
    assert result["fill_price"] == 100
