from quanter_swarm.decision.portfolio_optimizer import optimize_weights


def test_optimizer_penalizes_high_correlation_and_volatility() -> None:
    weights = optimize_weights(
        [
            {
                "leader": "momentum",
                "score": 0.8,
                "confidence": 0.9,
                "volatility": 0.05,
                "correlation": 0.9,
                "event_risk": 0.8,
            },
            {
                "leader": "stat_arb",
                "score": 0.7,
                "confidence": 0.8,
                "volatility": 0.02,
                "correlation": 0.2,
                "event_risk": 0.1,
            },
        ],
        gross_exposure=0.8,
        max_single_weight=0.8,
        allocation_mode="correlation_aware",
        correlation_penalty=0.6,
        turnover_penalty=0.1,
        event_penalty=0.4,
    )
    assert weights["stat_arb"] > weights["momentum"]
