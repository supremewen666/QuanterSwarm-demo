from quanter_swarm.orchestrator.ranking_engine import rank_candidates


def test_ranking_engine_sorts_descending() -> None:
    ranked = rank_candidates([{"score": 2}, {"score": 5}, {"score": 1}])
    assert [item["score"] for item in ranked] == [5, 2, 1]
