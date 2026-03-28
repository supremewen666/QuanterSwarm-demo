"""Readonly Alpaca adapter used only for dashboard enrichment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AlpacaDashboardSource:
    """Fetch readonly broker snapshots for dashboard display only."""

    enabled: bool = False
    base_url: str = "https://paper-api.alpaca.markets"
    data_url: str = "https://data.alpaca.markets"
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        self.base_url = os.getenv("ALPACA_BASE_URL", self.base_url).rstrip("/")

    def _headers(self) -> dict[str, str] | None:
        key_id = os.getenv("ALPACA_API_KEY_ID")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        if not key_id or not secret_key:
            return None
        return {
            "APCA-API-KEY-ID": key_id,
            "APCA-API-SECRET-KEY": secret_key,
        }

    def fetch_snapshot(self) -> dict[str, Any]:
        if not self.enabled:
            return {
                "enabled": False,
                "status": "disabled",
                "label": "external / read-only",
                "capabilities": ["account_snapshot", "positions_snapshot", "order_history"],
                "reason": "feature_flag_disabled",
                "updated_at": None,
                "account": None,
                "positions": [],
                "orders": [],
            }

        headers = self._headers()
        if headers is None:
            return {
                "enabled": True,
                "status": "degraded",
                "label": "external / read-only",
                "capabilities": ["account_snapshot", "positions_snapshot", "order_history"],
                "reason": "missing_credentials",
                "updated_at": None,
                "account": None,
                "positions": [],
                "orders": [],
            }

        try:
            import httpx

            with httpx.Client(base_url=self.base_url.rstrip("/"), headers=headers, timeout=self.timeout_seconds) as client:
                account_response = client.get("/v2/account")
                positions_response = client.get("/v2/positions")
                orders_response = client.get("/v2/orders", params={"status": "all", "limit": 20})
                account_response.raise_for_status()
                positions_response.raise_for_status()
                orders_response.raise_for_status()
        except ModuleNotFoundError:
            return {
                "enabled": True,
                "status": "degraded",
                "label": "external / read-only",
                "capabilities": ["account_snapshot", "positions_snapshot", "order_history"],
                "reason": "httpx_not_installed",
                "updated_at": None,
                "account": None,
                "positions": [],
                "orders": [],
            }
        except httpx.HTTPError as exc:
            return {
                "enabled": True,
                "status": "degraded",
                "label": "external / read-only",
                "capabilities": ["account_snapshot", "positions_snapshot", "order_history"],
                "reason": str(exc),
                "updated_at": None,
                "account": None,
                "positions": [],
                "orders": [],
            }

        return {
            "enabled": True,
            "status": "ok",
            "label": "external / read-only",
            "capabilities": ["account_snapshot", "positions_snapshot", "order_history"],
            "reason": "",
            "updated_at": account_response.headers.get("date"),
            "account": account_response.json(),
            "positions": positions_response.json(),
            "orders": orders_response.json(),
        }
