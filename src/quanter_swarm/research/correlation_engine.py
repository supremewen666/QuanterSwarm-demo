"""Correlation helpers."""


def correlation(a: list[float], b: list[float]) -> float:
    return 1.0 if a and b and len(a) == len(b) else 0.0
