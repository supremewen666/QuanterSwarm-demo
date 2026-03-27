from quanter_swarm.services.risk.engine import evaluate_risk_rules
from quanter_swarm.services.risk.rules import (
    earnings_no_trade_rule,
    max_daily_loss_rule,
    max_leverage_rule,
    max_position_size_rule,
    volatility_no_trade_rule,
)


def test_risk_rules_flag_expected_violations() -> None:
    portfolio = {"positions": [{"symbol": "AAPL", "weight": 0.2}], "gross_exposure": 1.2}

    assert max_position_size_rule(portfolio, 0.15) == "max_position_size"
    assert max_leverage_rule(portfolio, 1.0) == "max_leverage"
    assert max_daily_loss_rule(0.05, 0.03) == "max_daily_loss"
    assert earnings_no_trade_rule({"event_type": "earnings"}, True) == "earnings_no_trade"
    assert volatility_no_trade_rule(0.09, 0.08) == "volatility_no_trade"


def test_risk_engine_blocks_when_any_rule_triggers() -> None:
    result = evaluate_risk_rules(
        portfolio={"positions": [{"symbol": "AAPL", "weight": 0.2}], "gross_exposure": 0.2},
        market_packet={"volatility": 0.03},
        event_payload={},
        daily_loss_pct=0.0,
        rules_config={
            "max_position_size": 0.15,
            "max_leverage": 1.0,
            "max_daily_loss": 0.03,
            "earnings_no_trade": True,
            "volatility_no_trade": 0.08,
        },
    )

    assert result["status"] == "blocked"
    assert result["approved"] is False
    assert "max_position_size" in result["triggered_rules"]
