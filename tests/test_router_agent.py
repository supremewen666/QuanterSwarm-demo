from quanter_swarm.orchestrator.router_agent import RouterAgent


def test_router_agent_selects_route() -> None:
    route = RouterAgent().route(
        "trend_up",
        {"router": {"default_regime": "sideways", "token_budget": "medium"}},
        {"regimes": {"trend_up": {"leaders": ["momentum", "breakout_event"]}}},
    )
    assert route["leaders"] == ["momentum", "breakout_event"]


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
