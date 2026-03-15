"""Slippage helpers."""


def apply_slippage(price: float, bps: float) -> float:
    return price * (1 + bps / 10000)
