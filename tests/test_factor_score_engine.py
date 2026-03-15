from quanter_swarm.research.factor_score_engine import compute_factor_score


def test_factor_score_engine_sums_values() -> None:
    assert compute_factor_score({"a": 1, "b": 2}) == 1.5
