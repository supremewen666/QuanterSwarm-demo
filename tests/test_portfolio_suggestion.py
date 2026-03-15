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


def test_portfolio_suggestion_supports_multiple_allocation_modes() -> None:
    ideas = [
        {"symbol": "AAPL", "leader": "momentum", "score": 0.8, "volatility": 0.02, "correlation": 0.7},
        {"symbol": "AAPL", "leader": "stat_arb", "score": 0.7, "volatility": 0.01, "correlation": 0.2},
    ]
    simple = build_portfolio(ideas, allocation_mode="simple", cash_buffer=0.1, max_single_weight=0.8)
    vol_aware = build_portfolio(ideas, allocation_mode="volatility_aware", cash_buffer=0.1, max_single_weight=0.8)
    corr_aware = build_portfolio(ideas, allocation_mode="correlation_aware", cash_buffer=0.1, max_single_weight=0.8)
    assert simple["allocation_mode"] == "simple"
    assert vol_aware["allocation_mode"] == "volatility_aware"
    assert corr_aware["allocation_mode"] == "correlation_aware"
    assert vol_aware["positions"][0]["weight"] != simple["positions"][0]["weight"]
