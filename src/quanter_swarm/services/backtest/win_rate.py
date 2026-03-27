"""Win-rate metric."""


def win_rate(returns: list[float]) -> float:
    return len([value for value in returns if value > 0]) / len(returns) if returns else 0.0
