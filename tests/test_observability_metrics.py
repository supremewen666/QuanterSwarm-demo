from quanter_swarm.services.monitoring.metrics import build_cycle_metrics, estimate_token_cost


def test_estimate_token_cost_uses_agent_cost_hints() -> None:
    metrics = estimate_token_cost(
        leaders=["momentum"],
        specialists=["memory_compression", "risk"],
        token_budget="medium",
    )

    assert metrics["estimated_tokens"] > 0
    assert metrics["leaders"]["momentum"] > metrics["specialists"]["risk"]
    assert metrics["budget"] == "medium"


def test_build_cycle_metrics_exposes_required_metric_groups() -> None:
    metrics = build_cycle_metrics(
        state_latencies={
            "data_fetch": 10,
            "regime_detect": 4,
            "routing": 6,
            "agent_execution": 12,
            "risk_check": 3,
            "portfolio_build": 8,
            "report_generation": 5,
        },
        runtime_ms=48,
        leaders=["momentum"],
        specialists=["risk"],
        success=True,
        token_budget="low",
    )

    assert metrics["router_latency"]["routing_ms"] == 6
    assert metrics["agent_latency"]["agent_execution_ms"] == 12
    assert metrics["cycle_success_rate"]["value"] == 1.0
    assert metrics["token_cost"]["budget"] == "low"
