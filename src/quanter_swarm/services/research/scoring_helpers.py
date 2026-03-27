"""Scoring helpers."""


def normalize_score(value: float, floor: float = 0.0, ceiling: float = 1.0) -> float:
    return max(floor, min(value, ceiling))
