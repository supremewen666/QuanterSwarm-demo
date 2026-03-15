from quanter_swarm.orchestrator.router_agent import RouterAgent


def test_router_agent_selects_route() -> None:
    route = RouterAgent().route(
        "trend_up",
        {"router": {"default_regime": "sideways", "token_budget": "medium"}},
        {"regimes": {"trend_up": {"leaders": ["momentum", "breakout_event"]}}},
    )
    assert route["leaders"] == ["momentum", "breakout_event"]
