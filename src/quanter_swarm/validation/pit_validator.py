"""Point-in-time validation for research snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from quanter_swarm.errors import DataProviderError
from quanter_swarm.validation.data_integrity import (
    ensure_monotonic,
    ensure_not_future,
    parse_timestamp,
)


class PITValidator:
    def validate(self, snapshot: dict[str, Any]) -> None:
        as_of_ts = snapshot.get("as_of_ts")
        if as_of_ts is None:
            raise DataProviderError("Snapshot is missing as_of_ts.")
        as_of_dt = parse_timestamp(as_of_ts)

        self._validate_packet(snapshot, as_of_dt, "snapshot")
        for name in ("market_packet", "fundamentals_packet", "macro_inputs", "shares_float_packet"):
            packet = snapshot.get(name, {})
            if packet:
                self._validate_packet(packet, as_of_dt, name)

        for index, item in enumerate(snapshot.get("news_packet", [])):
            self._validate_packet(item, as_of_dt, f"news_packet[{index}]")

        for index, item in enumerate(snapshot.get("vintage_macro_packet", [])):
            self._validate_packet(item, as_of_dt, f"vintage_macro_packet[{index}]")
            vintage_date = item.get("vintage_date")
            if vintage_date:
                ensure_not_future(vintage_date, upper_bound=as_of_dt, field_name=f"vintage_macro_packet[{index}].vintage_date")

    def _validate_packet(self, packet: dict[str, Any], as_of_dt: datetime, label: str) -> None:
        available_at = packet.get("available_at")
        if available_at:
            ensure_not_future(available_at, upper_bound=as_of_dt, field_name=f"{label}.available_at")
        ingested_at = packet.get("ingested_at")
        if ingested_at:
            ensure_not_future(ingested_at, upper_bound=as_of_dt, field_name=f"{label}.ingested_at")
        if available_at and ingested_at:
            ensure_monotonic(available_at, ingested_at, older_name=f"{label}.available_at", newer_name=f"{label}.ingested_at")
