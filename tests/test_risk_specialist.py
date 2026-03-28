from quanter_swarm.agents.specialists import RiskSpecialist


def test_risk_specialist_approves_placeholder_proposal() -> None:
    assert RiskSpecialist().assess({"volatility": 0.02, "macro_risk": 0.2})["approved"] is True
