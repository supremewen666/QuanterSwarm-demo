from quanter_swarm.decision.portfolio_suggestion import build_portfolio


def test_portfolio_suggestion_returns_positions() -> None:
    portfolio = build_portfolio([{"symbol": "AAPL", "leader": "momentum", "score": 0.8}], cash_buffer=0.1, max_single_weight=0.25)
    assert portfolio["positions"][0]["symbol"] == "AAPL"


def test_portfolio_suggestion_supports_reduced_exposure() -> None:
    portfolio = build_portfolio(
        [{"symbol": "AAPL", "leader": "momentum", "score": 0.8}],
        cash_buffer=0.1,
        max_single_weight=0.5,
        exposure_multiplier=0.5,
    )
    assert portfolio["mode"] == "reduced_exposure"
    assert portfolio["gross_exposure"] == 0.45
