from quanter_swarm.orchestrator.router_agent import RouterAgent


def test_router_agent_selects_route() -> None:
    route = RouterAgent().route(
        "trend_up",
        {"router": {"default_regime": "sideways", "token_budget": "medium"}},
        {"regimes": {"trend_up": {"leaders": ["momentum", "breakout_event"]}}},
    )
    assert route["leaders"] == ["momentum", "breakout_event"]
    assert route["leader_selected"] == ["momentum", "breakout_event"]
    assert route["confidence"] == 1.0


def test_router_agent_uses_flat_config_defaults() -> None:
    route = RouterAgent().route(
        "panic",
        {
            "default_regime": "high_vol",
            "token_budget": "low",
            "max_active_leaders": 1,
        },
        {
            "regimes": {
                "panic": {"leaders": []},
                "high_vol": {"leaders": ["breakout_event", "mean_reversion"]},
            }
        },
    )
    assert route["leaders"] == ["breakout_event"]
    assert route["token_budget"] == "low"
    assert route["reasons"]["breakout_event"].startswith("fallback_from_")


def test_router_agent_applies_low_confidence_policy() -> None:
    route = RouterAgent().route(
        {"label": "trend_up", "confidence": 0.3},
        {
            "confidence_threshold": 0.5,
            "low_confidence_policy": "fallback",
            "max_active_leaders": 2,
        },
        {
            "regimes": {
                "trend_up": {
                    "leaders": ["momentum", "breakout_event"],
                    "fallback_leaders": ["momentum"],
                }
            }
        },
    )
    assert route["leaders"] == ["momentum"]
    assert route["low_confidence_mode"] is True
    assert route["selected_reasons"]["momentum"] == "low_regime_confidence_fallback_leader"
    assert route["reasons"]["momentum"] == "low_regime_confidence_fallback_leader"


def test_router_agent_filters_leaders_by_capability() -> None:
    route = RouterAgent().route(
        "trend_down",
        {"default_regime": "sideways"},
        {
            "regimes": {
                "trend_down": {
                    "leaders": ["momentum", "mean_reversion"],
                    "weights": {"momentum": 0.5, "mean_reversion": 0.5},
                }
            }
        },
    )
    assert route["leaders"] == ["mean_reversion"]
    assert route["skipped_reasons"]["momentum"] == "unsupported_regime_capability"
    assert route["rejected_candidates"]["momentum"] == "unsupported_regime_capability"
