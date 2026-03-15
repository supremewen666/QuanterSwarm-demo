"""Fill helpers."""


def build_fill(order_id: str, price: float) -> dict:
    return {"order_id": order_id, "price": price}
