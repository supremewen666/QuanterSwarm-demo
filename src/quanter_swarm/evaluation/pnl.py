"""PnL metric."""


def pnl(returns: list[float]) -> float:
    return sum(returns)
