from quanter_swarm.decision.risk_guardrail import assess_guardrails, passes_guardrails


def test_risk_guardrail_blocks_warnings() -> None:
    assert passes_guardrails({"warnings": ["limit"]}) is False


def test_risk_guardrail_supports_reduced_exposure() -> None:
    result = assess_guardrails({"warnings": ["high_volatility"]})
    assert result["status"] == "reduced"
    assert result["exposure_multiplier"] == 0.5
