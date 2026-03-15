"""Slippage helpers."""


def apply_slippage(price: float, bps: float) -> float:
    return price * (1 + bps / 10000)


def estimate_slippage_bps(
    *,
    base_bps: float,
    volatility: float,
    participation_rate: float,
    is_open: bool,
) -> float:
    vol_component = max(0.0, volatility) * 180
    participation_component = max(0.0, participation_rate) * 250
    open_penalty = 6.0 if is_open else 0.0
    return round(max(0.0, base_bps + vol_component + participation_component + open_penalty), 4)
