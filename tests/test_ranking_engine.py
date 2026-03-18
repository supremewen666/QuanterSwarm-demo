from quanter_swarm.orchestrator.ranking_engine import rank_candidates


def test_ranking_engine_sorts_descending() -> None:
    ranked = rank_candidates([{"score": 2}, {"score": 5}, {"score": 1}])
    assert [item["score"] for item in ranked] == [5, 2, 1]


def test_ranking_engine_uses_posterior_score_when_available() -> None:
    ranked = rank_candidates(
        [
            {"leader": "a", "score": 0.8, "prior_score": -0.5, "risk_penalty": 0.1, "cost_penalty": 0.1},
            {"leader": "b", "score": 0.5, "prior_score": 0.25, "risk_penalty": 0.02, "cost_penalty": 0.01},
        ]
    )
    assert ranked[0]["leader"] == "b"
    assert ranked[0]["posterior_score"] > ranked[1]["posterior_score"]
