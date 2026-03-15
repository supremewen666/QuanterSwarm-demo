"""Factor scoring."""


def compute_factor_score(factors: dict) -> float:
    if not factors:
        return 0.0
    return round(float(sum(factors.values()) / len(factors)), 2)
