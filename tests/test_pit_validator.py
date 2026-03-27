import pytest

from quanter_swarm.backtest.cost_model import BacktestCostModel
from quanter_swarm.backtest.execution_simulator import ExecutionSimulator
from quanter_swarm.backtest.models import Fill
from quanter_swarm.backtest.validator import BacktestValidator
from quanter_swarm.errors import BacktestError, DataProviderError
from quanter_swarm.services.snapshot.builder import build_snapshot
from quanter_swarm.validation.pit_validator import PITValidator


def test_pit_validator_accepts_snapshot() -> None:
    snapshot = build_snapshot("AAPL")

    PITValidator().validate(snapshot)


def test_pit_validator_rejects_future_news() -> None:
    snapshot = build_snapshot("AAPL")
    snapshot["news_packet"][0]["available_at"] = "2999-01-01T00:00:00+00:00"

    with pytest.raises(DataProviderError):
        PITValidator().validate(snapshot)


def test_backtest_validator_rejects_empty_symbol_list() -> None:
    with pytest.raises(BacktestError):
        BacktestValidator().validate_run(
            {
                "symbols": [],
                "steps": 1,
                "train_window": 1,
                "test_window": 1,
                "rolling_window": 1,
                "capital": 1_000,
            }
        )


def test_backtest_cost_model_exposes_spread_cost() -> None:
    fills = [
        Fill(
            order_id="paper_1",
            status="accepted",
            fill_price=100.0,
            fill_ratio=1.0,
            total_cost=2.5,
            filled_notional=1_000.0,
        )
    ]

    cost_model = BacktestCostModel(spread_bps=2.0)

    assert cost_model.transaction_cost(fills) == 2.5
    assert cost_model.spread_cost(fills) == 0.2


def test_execution_simulator_handles_delayed_fills() -> None:
    result = ExecutionSimulator().simulate(
        {
            "decision_price": 100.0,
            "notional": 200_000.0,
            "avg_volume": 1_000_000.0,
            "volatility": 0.08,
            "event_window": True,
        }
    )

    assert result["status"] == "delayed"
    assert result["fill_ratio"] <= 0.5
