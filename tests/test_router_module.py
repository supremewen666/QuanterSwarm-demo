from quanter_swarm.agents.router import (
    detect_regime,
    regime_family_for,
    select_leader,
    select_specialist_plan,
    select_specialists,
)


def test_detect_regime_returns_stable_detail_payload() -> None:
    detail = detect_regime({"avg_change_pct": 0.01, "volatility": 0.02, "macro_risk": 0.3})
    assert detail["label"] in {"trend_up", "sideways", "risk_on", "high_vol"}
    assert detail["family"] in {"bull", "bear", "sideways", "volatile"}
    assert set(detail["family_candidates"]) == {"bull", "bear", "sideways", "volatile"}
    assert 0.0 <= detail["confidence"] <= 1.0
    assert "supporting_features" in detail


def test_regime_family_maps_legacy_labels_to_canonical_buckets() -> None:
    assert regime_family_for("trend_up") == "bull"
    assert regime_family_for("risk_off") == "bear"
    assert regime_family_for("panic") == "volatile"
    assert regime_family_for("sideways") == "sideways"


def test_select_leader_respects_regime_capability() -> None:
    route = select_leader(
        "trend_down",
        {"default_regime": "sideways"},
        {"regimes": {"trend_down": {"leaders": ["momentum", "mean_reversion"]}}},
    )
    assert route["leaders"] == ["mean_reversion"]
    assert route["skipped_reasons"]["momentum"] == "unsupported_regime_capability"


def test_select_specialists_filters_by_task() -> None:
    specialists = select_specialists("trend_up", task="risk_assessment")
    assert "risk" in specialists
    assert "data_fetch" not in specialists


def test_select_specialists_respects_budget_limits() -> None:
    plan = select_specialist_plan(
        "trend_up",
        router_config={
            "token_budget": "low",
            "latency_budget": "tight",
            "max_specialists_per_cycle": 3,
        },
    )
    assert plan["selected"] == ["risk"]
    assert plan["budget_constraints"]["token_budget_limit"] == 1
    assert plan["budget_constraints"]["latency_budget_limit"] == 1
    assert plan["rejected"]["data_fetch"] == "dropped_by_token_budget"
