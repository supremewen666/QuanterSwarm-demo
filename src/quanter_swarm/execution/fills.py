"""Fill helpers."""


def build_fill(order_id: str, price: float) -> dict:
    return {"order_id": order_id, "price": price}


def estimate_fill_ratio(
    *,
    participation_rate: float,
    volatility: float,
    fill_model: str = "partial",
) -> float:
    if fill_model == "full":
        return 1.0
    base = 1.0 - participation_rate * 1.8 - volatility * 4.0
    return round(max(0.35, min(1.0, base)), 4)
