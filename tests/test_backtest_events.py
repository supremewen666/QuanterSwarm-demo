from quanter_swarm.agents.orchestrator.root_agent import RootAgent
from quanter_swarm.backtest.events import (
    FillEvent,
    MarketEvent,
    OrderEvent,
    PortfolioUpdateEvent,
    SignalEvent,
)
from quanter_swarm.backtest.replay_engine import emit_replay_events


def test_backtest_event_models_validate() -> None:
    market = MarketEvent(symbol="AAPL", payload={"price": 100.0})
    signal = SignalEvent(symbol="AAPL", payload={"leader": "momentum"})
    order = OrderEvent(symbol="AAPL", payload={"symbol": "AAPL", "notional": 1000})
    fill = FillEvent(symbol="AAPL", payload={"fill_price": 100.1})
    portfolio = PortfolioUpdateEvent(symbol="AAPL", payload={"mode": "paper"})

    assert market.event_type == "market"
    assert signal.event_type == "signal"
    assert order.event_type == "order"
    assert fill.event_type == "fill"
    assert portfolio.event_type == "portfolio_update"


def test_replay_engine_emits_event_sequence() -> None:
    report = RootAgent().run_sync("AAPL")
    events = emit_replay_events(report, 100_000)
    event_types = [event["event_type"] for event in events]
    assert event_types[0] == "market"
    assert "signal" in event_types
    assert "portfolio_update" in event_types
