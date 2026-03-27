"""Stability metric."""


def stability_score(values: list[float]) -> float:
    if not values:
        return 0.0
    sign_flips = sum(1 for idx in range(1, len(values)) if values[idx] * values[idx - 1] < 0)
    return round(max(0.0, 1 - sign_flips / max(1, len(values) - 1)), 4)
