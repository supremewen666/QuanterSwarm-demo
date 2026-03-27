"""Audit log helpers."""


def audit(entry: dict) -> dict:
    return {
        "order_intent": entry.get("order_intent", {}),
        "fill_assumption": entry.get("fill_assumption", {}),
        "slippage_amount": round(float(entry.get("slippage_amount", 0.0)), 6),
        "total_cost": round(float(entry.get("total_cost", 0.0)), 6),
        "execution_summary": entry.get("execution_summary", {}),
    }
