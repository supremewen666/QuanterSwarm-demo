"""Sortino metric."""


def sortino_ratio(returns: list[float]) -> float:
    downside = [value for value in returns if value < 0]
    return sum(returns) / max(len(downside), 1) if returns else 0.0
