"""Drawdown metric."""


def max_drawdown(series: list[float]) -> float:
    peak = 0.0
    worst = 0.0
    cumulative = 0.0
    for value in series:
        cumulative += value
        peak = max(peak, cumulative)
        worst = min(worst, cumulative - peak)
    return round(abs(worst), 4)
