"""Order sizing."""


def size_order(weight: float, capital: float) -> float:
    return max(0.0, round(weight * capital, 2))
