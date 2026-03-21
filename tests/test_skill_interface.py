from quanter_swarm.contracts import CycleReport, ResearchRequestContract
from quanter_swarm.skill_interface import run_skill, run_skill_request


def test_skill_interface_returns_fixed_contract_fields() -> None:
    response = run_skill_request({"symbol": "AAPL"}, mode="normal")
    assert response["regime"]
    assert "active_leaders" in response
    assert "decision_trace_summary" in response


def test_skill_interface_missing_data_mode_marks_fallback() -> None:
    response = run_skill_request({"symbol": "AAPL"}, mode="missing_data")
    fallback = response["decision_trace_summary"]["fallback_modes"]
    assert "sentiment_fallback" in fallback
    assert "fundamentals_fallback" in fallback


def test_skill_interface_no_trade_mode_forces_no_trade() -> None:
    response = run_skill_request({"symbol": "AAPL"}, mode="no_trade")
    assert response["portfolio_suggestion"]["mode"] == "no_trade"


def test_run_skill_returns_strict_cycle_report() -> None:
    report = run_skill(ResearchRequestContract(symbol="AAPL"))

    assert isinstance(report, CycleReport)
    assert report.symbol == "AAPL"


def test_skill_interface_accepts_policy_override() -> None:
    response = run_skill_request(
        {"symbol": "AAPL"},
        policy={"llm_provider_override": "mock", "llm_model_override": "mock-echo", "tool_timeout": 3},
    )

    assert response["symbol"] == "AAPL"
