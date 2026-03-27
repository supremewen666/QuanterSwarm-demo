"""Sharpe metric."""

from math import sqrt


def sharpe_ratio(returns: list[float]) -> float:
    if not returns:
        return 0.0
    avg = sum(returns) / len(returns)
    variance = sum((value - avg) ** 2 for value in returns) / len(returns)
    if variance == 0:
        return round(avg, 4)
    return float(round(avg / (variance ** 0.5) * sqrt(len(returns)), 4))
