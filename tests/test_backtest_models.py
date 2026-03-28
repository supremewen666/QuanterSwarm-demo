from quanter_swarm.agents.orchestrator import RootAgent
from quanter_swarm.backtest.models import Fill, Order, Portfolio, Position
from quanter_swarm.backtest.replay_engine import replay_report


def test_backtest_models_validate_core_objects() -> None:
    order = Order(symbol="AAPL", leader="momentum", notional=10_000, decision_price=100.0)
    fill = Fill(order_id="paper_1", status="accepted", fill_price=100.2, fill_ratio=1.0, total_cost=5.0)
    position = Position(symbol="AAPL", leader="momentum", weight=0.25)
    portfolio = Portfolio(
        positions=[position],
        gross_exposure=0.25,
        cash_buffer=0.75,
        mode="paper",
        allocation_mode="simple",
    )

    assert order.symbol == "AAPL"
    assert fill.total_cost == 5.0
    assert portfolio.positions[0].leader == "momentum"


def test_replay_report_uses_portfolio_and_fill_models() -> None:
    report = RootAgent().run_sync("AAPL")
    replay = replay_report(report, 100_000)
    assert "realized_return" in replay
    assert "portfolio_attribution" in replay
    assert replay["portfolio_attribution"]["mode"] in {"paper", "reduced_exposure", "no_trade"}
