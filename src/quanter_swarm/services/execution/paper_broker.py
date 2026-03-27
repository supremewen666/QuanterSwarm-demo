"""Paper broker."""

from __future__ import annotations

from pathlib import Path

from quanter_swarm.core.runtime.config import load_yaml
from quanter_swarm.core.runtime.ids import new_id
from quanter_swarm.services.execution.audit_log import audit
from quanter_swarm.services.execution.fills import decide_fill_status, estimate_fill_ratio
from quanter_swarm.services.execution.slippage import apply_slippage, estimate_slippage_bps


class PaperBroker:
    def __init__(self, config_dir: Path | None = None) -> None:
        root = config_dir or Path("configs")
        paper_cfg = load_yaml(root / "paper_broker.yaml").get("paper_broker", {})
        exec_cfg = load_yaml(root / "execution.yaml").get("execution", {})
        self.base_slippage_bps = float(paper_cfg.get("slippage_bps", 5))
        self.commission_per_trade = float(paper_cfg.get("commission_per_trade", 0.0))
        self.commission_bps = float(paper_cfg.get("commission_bps", 0.0))
        self.fill_model = str(paper_cfg.get("fill_model", "partial"))
        self.gap_sensitivity = float(paper_cfg.get("gap_sensitivity", 0.3))
        self.open_session_penalty = float(paper_cfg.get("open_session_penalty_bps", 6.0))
        self.default_assume_open = bool(exec_cfg.get("assume_open_session", False))

    def submit(self, order: dict) -> dict:
        decision_price = float(order.get("decision_price", order.get("reference_price", 0.0)))
        notional = float(order.get("notional", 0.0))
        avg_volume = max(1.0, float(order.get("avg_volume", 1_000_000.0)))
        participation_rate = max(0.0, min(2.0, notional / avg_volume))
        volatility = max(0.0, float(order.get("volatility", 0.0)))
        gap_pct = float(order.get("gap_pct", 0.0))
        is_open = bool(order.get("is_open_session", self.default_assume_open))
        event_window = bool(order.get("event_window", False))

        effective_slippage_bps = estimate_slippage_bps(
            base_bps=self.base_slippage_bps + (self.open_session_penalty if is_open else 0.0),
            volatility=volatility,
            participation_rate=participation_rate,
            is_open=is_open,
        )
        execution_price = decision_price * (1 + gap_pct * self.gap_sensitivity)
        fill_price = apply_slippage(execution_price, effective_slippage_bps)
        fill_ratio = estimate_fill_ratio(
            participation_rate=participation_rate,
            volatility=volatility,
            fill_model=self.fill_model,
        )
        status = decide_fill_status(
            participation_rate=participation_rate,
            volatility=volatility,
            event_window=event_window,
            fill_ratio=fill_ratio,
        )
        if status == "unfilled":
            fill_ratio = 0.0
        if status == "delayed":
            fill_ratio = min(fill_ratio, 0.5)
        filled_notional = notional * fill_ratio
        commission_cost = self.commission_per_trade + filled_notional * self.commission_bps / 10000
        slippage_cost = max(0.0, filled_notional * max(0.0, fill_price - decision_price) / max(0.01, decision_price))

        audit_entry = audit(
            {
                "order_intent": {
                    "symbol": order.get("symbol"),
                    "leader": order.get("leader"),
                    "notional": notional,
                    "decision_price": decision_price,
                },
                "fill_assumption": {
                    "fill_model": self.fill_model,
                    "fill_ratio": fill_ratio,
                    "participation_rate": round(participation_rate, 6),
                    "slippage_bps": effective_slippage_bps,
                    "is_open_session": is_open,
                    "gap_pct": gap_pct,
                    "event_window": event_window,
                },
                "slippage_amount": slippage_cost,
                "total_cost": slippage_cost + commission_cost,
                "execution_summary": {
                    "execution_price": round(execution_price, 6),
                    "realized_fill_price": round(fill_price, 6),
                    "filled_notional": round(filled_notional, 6),
                    "commission_cost": round(commission_cost, 6),
                },
            }
        )

        return {
            "status": status,
            "order_id": new_id("paper"),
            "order": order,
            "decision_price": round(decision_price, 6),
            "execution_price": round(execution_price, 6),
            "fill_price": round(fill_price, 6),
            "fill_ratio": fill_ratio,
            "filled_notional": round(filled_notional, 6),
            "slippage_bps": effective_slippage_bps,
            "commission_cost": round(commission_cost, 6),
            "total_cost": round(slippage_cost + commission_cost, 6),
            "audit": audit_entry,
        }
