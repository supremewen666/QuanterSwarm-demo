from quanter_swarm.services.portfolio.suggestion import build_portfolio


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


def test_portfolio_suggestion_penalizes_high_correlation() -> None:
    ideas = [
        {"symbol": "AAPL", "leader": "momentum", "score": 0.8, "confidence": 0.9, "volatility": 0.02, "correlation": 0.95},
        {"symbol": "AAPL", "leader": "stat_arb", "score": 0.75, "confidence": 0.85, "volatility": 0.02, "correlation": 0.2},
    ]
    portfolio = build_portfolio(ideas, allocation_mode="correlation_aware", max_single_weight=0.8, cash_buffer=0.1)
    weights = {position["leader"]: position["weight"] for position in portfolio["positions"]}
    assert weights["stat_arb"] > weights["momentum"]


def test_portfolio_suggestion_penalizes_high_volatility() -> None:
    ideas = [
        {"symbol": "AAPL", "leader": "momentum", "score": 0.8, "confidence": 0.9, "volatility": 0.08, "correlation": 0.2},
        {"symbol": "AAPL", "leader": "mean_reversion", "score": 0.7, "confidence": 0.8, "volatility": 0.02, "correlation": 0.2},
    ]
    portfolio = build_portfolio(ideas, allocation_mode="volatility_aware", max_single_weight=0.8, cash_buffer=0.1)
    weights = {position["leader"]: position["weight"] for position in portfolio["positions"]}
    assert weights["mean_reversion"] > weights["momentum"]


def test_portfolio_suggestion_no_trade_is_explicit() -> None:
    portfolio = build_portfolio([], exposure_multiplier=0.0)
    assert portfolio["mode"] == "no_trade"
    assert portfolio["no_trade_reason"] in {"low_signal_or_blocked_exposure", "scaled_to_zero"}


def test_portfolio_suggestion_risk_off_increases_cash_buffer() -> None:
    ideas = [{"symbol": "AAPL", "leader": "momentum", "score": 0.9, "confidence": 0.9, "volatility": 0.03, "correlation": 0.3}]
    portfolio = build_portfolio(
        ideas,
        regime="risk_off",
        regime_overrides={"risk_off": {"cash_buffer": 0.4, "exposure_multiplier": 0.5, "target_positions": 1}},
        cash_buffer=0.1,
    )
    assert portfolio["cash_buffer"] >= 0.4
