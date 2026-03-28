from quanter_swarm.agents.orchestrator import RootAgent
from quanter_swarm.backtest.costs import slippage, transaction_fee
from quanter_swarm.backtest.models import Fill
from quanter_swarm.backtest.replay_engine import replay_report


def test_backtest_cost_model_sums_transaction_fees_and_slippage() -> None:
    fills = [
        Fill(
            order_id="paper_1",
            status="accepted",
            fill_price=100.2,
            fill_ratio=1.0,
            total_cost=2.5,
            filled_notional=1000.0,
        ),
        Fill(
            order_id="paper_2",
            status="partial",
            fill_price=50.1,
            fill_ratio=0.5,
            total_cost=1.25,
            filled_notional=500.0,
        ),
    ]
    assert transaction_fee(fills) == 3.75
    assert slippage(fills) == 3.75


def test_replay_report_exposes_cost_breakdown() -> None:
    report = RootAgent().run_sync("AAPL")
    replay = replay_report(report, 100_000)
    assert "transaction_fee" in replay
    assert "slippage" in replay
    assert replay["cost_ratio"] >= 0.0
