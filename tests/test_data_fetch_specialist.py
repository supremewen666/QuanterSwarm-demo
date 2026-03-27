from quanter_swarm.agents.specialists.data_fetch_specialist import DataFetchSpecialist


def test_data_fetch_specialist_returns_symbol() -> None:
    assert DataFetchSpecialist().fetch("MSFT")["symbol"] == "MSFT"


def test_data_fetch_specialist_returns_normalized_packets() -> None:
    packet = DataFetchSpecialist().fetch("MSFT")
    assert packet["market_packet"]["price"] is not None
    assert packet["fundamentals_packet"]["symbol"] == "MSFT"
    assert len(packet["news_inputs"]) == 2
