from quanter_swarm.agents.leaders import BreakoutEventLeader, MomentumLeader
from quanter_swarm.agents.specialists import RiskSpecialist


def test_leader_exposes_capability_metadata() -> None:
    leader = MomentumLeader()
    assert leader.supported_regimes
    assert leader.supported_tasks
    assert leader.cost_hint == "medium"
    assert leader.priority > 0
    assert leader.supports_regime("trend_up") is True
    assert leader.supports_regime("risk_off") is False


def test_breakout_leader_supports_high_vol_regimes() -> None:
    leader = BreakoutEventLeader()
    assert leader.supports_regime("high_vol") is True
    assert leader.supports_task("event_breakout") is True


def test_specialist_exposes_task_metadata() -> None:
    specialist = RiskSpecialist()
    assert specialist.supported_tasks
    assert specialist.cost_hint == "low"
    assert specialist.priority >= 90
    assert specialist.supports_task("risk_assessment") is True
