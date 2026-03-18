"""Point-in-time snapshot builder."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from time import time

from quanter_swarm.data.base import BaseDataProvider, get_default_data_provider
from quanter_swarm.data.reliability import compute_source_reliability
from quanter_swarm.data.schemas import make_metadata


def _merge_metadata(payload: dict, metadata: dict) -> dict:
    merged = {**payload, **metadata}
    reliability = compute_source_reliability(merged)
    merged["reliability_score"] = reliability["reliability_score"]
    merged["quality_flags"] = sorted(set(merged.get("quality_flags", []) + reliability["quality_flags"]))
    merged["reliability_breakdown"] = reliability
    return merged


def _market_record(symbol: str, provider: BaseDataProvider, as_of_ts: int, latest: dict | None = None) -> dict:
    latest = latest or provider.get_latest_price(symbol)
    metadata = make_metadata(
        as_of_ts=as_of_ts,
        source=getattr(provider, "data_source", provider.__class__.__name__.lower()),
        source_type=getattr(provider, "source_type", "derived"),
        record_key=f"market:{symbol.upper()}",
        available_at=latest.get("ts_available") or latest.get("available_at"),
        ingested_at=latest.get("ts_event") or latest.get("ingested_at"),
        quality_flags=list(latest.get("quality_flags", [])),
    ).as_dict()
    return _merge_metadata(
        {
            "symbol": latest["symbol"],
            "price": latest["price"],
            "avg_volume": latest["avg_volume"],
            "change_pct": latest["change_pct"],
            "volatility": latest["volatility"],
            "closes": list(latest.get("closes", [])),
            "vendor_symbol": latest.get("vendor_symbol", latest["symbol"]),
            "adjustment_factor": latest.get("adjustment_factor", 1.0),
            "latency_ms": latest.get("latency_ms", 0),
        },
        metadata,
    )


def _fundamentals_record(symbol: str, provider: BaseDataProvider, as_of_ts: int, fundamentals: dict | None = None) -> dict:
    fundamentals = fundamentals or provider.get_fundamentals(symbol)
    metadata = make_metadata(
        as_of_ts=as_of_ts,
        source=fundamentals.get("source", getattr(provider, "data_source", "provider")),
        source_type="official",
        record_key=f"fundamentals:{symbol.upper()}",
        available_at=fundamentals.get("available_at"),
        ingested_at=fundamentals.get("accepted_at") or fundamentals.get("filed_at"),
        quality_flags=["xbrl_normalized"] if not fundamentals.get("restatement_flag") else ["restated"],
    ).as_dict()
    return _merge_metadata(fundamentals, metadata)


def _macro_record(symbol: str, provider: BaseDataProvider, as_of_ts: int, macro: dict | None = None) -> dict:
    macro = macro or provider.get_macro(symbol)
    metadata = make_metadata(
        as_of_ts=as_of_ts,
        source=macro.get("source", "macro"),
        source_type="official",
        record_key=f"macro:{symbol.upper()}",
        available_at=macro.get("available_at") or macro.get("release_time"),
        ingested_at=macro.get("release_time"),
        quality_flags=["vintage_tracked"],
    ).as_dict()
    return _merge_metadata(macro, metadata)


def _news_records(symbol: str, provider: BaseDataProvider, as_of_ts: int, news: list[dict] | None = None) -> list[dict]:
    items = []
    for index, item in enumerate(news or provider.get_news(symbol)):
        metadata = make_metadata(
            as_of_ts=as_of_ts,
            source=item.get("source", getattr(provider, "data_source", "provider")),
            source_type="commercial",
            record_key=f"news:{symbol.upper()}:{index}",
            available_at=item.get("published_at"),
            ingested_at=item.get("ingested_at"),
            quality_flags=list(item.get("quality_flags", [])),
        ).as_dict()
        enriched = _merge_metadata(item, metadata)
        if datetime.fromisoformat(enriched["available_at"]).timestamp() <= as_of_ts:
            items.append(enriched)
    return items


def build_snapshot(symbol: str, provider: BaseDataProvider | None = None) -> dict:
    resolved_provider = provider or get_default_data_provider()
    as_of_ts = int(time())
    market_packet = _market_record(symbol, resolved_provider, as_of_ts)
    price_history = resolved_provider.get_price_history(symbol)
    fundamentals_packet = _fundamentals_record(symbol, resolved_provider, as_of_ts)
    news_items = _news_records(symbol, resolved_provider, as_of_ts)
    macro_inputs = _macro_record(symbol, resolved_provider, as_of_ts)
    shares_float_packet = resolved_provider.get_shares_float(symbol)
    sec_filings_packet = resolved_provider.get_filings(symbol)
    vintage_macro_packet = resolved_provider.get_macro_vintages(symbol)
    quality_flags = sorted(
        set(
            market_packet.get("quality_flags", [])
            + fundamentals_packet.get("quality_flags", [])
            + macro_inputs.get("quality_flags", [])
            + [flag for item in news_items for flag in item.get("quality_flags", [])]
            + (["missing_vintage_macro"] if not vintage_macro_packet else [])
        )
    )
    evidence = {
        "market": {
            "source": market_packet["source"],
            "available_at": market_packet["available_at"],
            "reliability_score": market_packet["reliability_score"],
        },
        "fundamentals": {
            "source": fundamentals_packet["source"],
            "available_at": fundamentals_packet["available_at"],
            "reliability_score": fundamentals_packet["reliability_score"],
            "restatement_risk": fundamentals_packet.get("restatement_flag", False),
        },
        "macro": {
            "source": macro_inputs["source"],
            "available_at": macro_inputs["available_at"],
            "reliability_score": macro_inputs["reliability_score"],
        },
        "shares_float": shares_float_packet,
        "sec_filings_count": len(sec_filings_packet),
        "macro_vintages_count": len(vintage_macro_packet),
        "news": [
            {
                "source": item["source"],
                "available_at": item["available_at"],
                "reliability_score": item["reliability_score"],
                "headline": item["headline"],
            }
            for item in news_items
        ],
    }
    snapshot = {
        "symbol": symbol.upper(),
        "as_of_ts": as_of_ts,
        "timestamp": datetime.fromtimestamp(as_of_ts, tz=UTC).isoformat(),
        "data_source": getattr(resolved_provider, "data_source", resolved_provider.__class__.__name__.lower()),
        "available_at": max(
            market_packet["available_at"],
            fundamentals_packet["available_at"],
            macro_inputs["available_at"],
        ),
        "ingested_at": datetime.fromtimestamp(as_of_ts, tz=UTC).isoformat(),
        "source": getattr(resolved_provider, "data_source", resolved_provider.__class__.__name__.lower()),
        "source_type": getattr(resolved_provider, "source_type", "derived"),
        "record_id": f"snapshot:{symbol.upper()}:{as_of_ts}",
        "schema_version": "2026-03-18",
        "quality_flags": quality_flags,
        "reliability_score": round(
            (
                market_packet["reliability_score"]
                + fundamentals_packet["reliability_score"]
                + macro_inputs["reliability_score"]
                + (sum(item["reliability_score"] for item in news_items) / max(1, len(news_items)))
            )
            / 4,
            4,
        ),
        "market_packet": {
            "symbol": market_packet["symbol"],
            "price": market_packet["price"],
            "closes": [row["close"] for row in price_history] or market_packet["closes"],
            "avg_volume": market_packet["avg_volume"],
            "change_pct": market_packet["change_pct"],
            "volatility": market_packet["volatility"],
            "available_at": market_packet["available_at"],
            "source": market_packet["source"],
            "source_type": market_packet["source_type"],
            "record_id": market_packet["record_id"],
            "schema_version": market_packet["schema_version"],
            "quality_flags": market_packet["quality_flags"],
            "reliability_score": market_packet["reliability_score"],
        },
        "fundamentals_packet": fundamentals_packet,
        "shares_float_packet": shares_float_packet,
        "sec_filings_packet": sec_filings_packet,
        "vintage_macro_packet": vintage_macro_packet,
        "news_packet": news_items,
        "news_inputs": [item["headline"] for item in news_items],
        "macro_inputs": macro_inputs,
        "evidence": evidence,
    }
    snapshot["snapshot_hash"] = sha256(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return snapshot


def build_snapshots(symbols: list[str], provider: BaseDataProvider | None = None) -> dict[str, dict]:
    resolved_provider = provider or get_default_data_provider()
    as_of_ts = int(time())
    normalized = [symbol.upper() for symbol in symbols]
    latest_prices = resolved_provider.get_latest_prices(normalized)
    histories = resolved_provider.get_price_histories(normalized)
    fundamentals_batch = resolved_provider.get_fundamentals_batch(normalized)
    news_batch = resolved_provider.get_news_batch(normalized)
    macro_batch = resolved_provider.get_macro_batch(normalized)
    shares_float_batch = resolved_provider.get_shares_float_batch(normalized)
    filings_batch = resolved_provider.get_filings_batch(normalized)
    vintage_macro_batch = resolved_provider.get_macro_vintages_batch(normalized)
    snapshots: dict[str, dict] = {}
    for symbol in normalized:
        market_packet = _market_record(symbol, resolved_provider, as_of_ts, latest=latest_prices[symbol])
        price_history = histories.get(symbol, [])
        fundamentals_packet = _fundamentals_record(
            symbol,
            resolved_provider,
            as_of_ts,
            fundamentals=fundamentals_batch[symbol],
        )
        news_items = _news_records(symbol, resolved_provider, as_of_ts, news=news_batch.get(symbol, []))
        macro_inputs = _macro_record(symbol, resolved_provider, as_of_ts, macro=macro_batch[symbol])
        shares_float_packet = shares_float_batch.get(symbol, {})
        sec_filings_packet = filings_batch.get(symbol, [])
        vintage_macro_packet = vintage_macro_batch.get(symbol, [])
        quality_flags = sorted(
            set(
                market_packet.get("quality_flags", [])
                + fundamentals_packet.get("quality_flags", [])
                + macro_inputs.get("quality_flags", [])
                + [flag for item in news_items for flag in item.get("quality_flags", [])]
                + (["missing_vintage_macro"] if not vintage_macro_packet else [])
            )
        )
        evidence = {
            "market": {
                "source": market_packet["source"],
                "available_at": market_packet["available_at"],
                "reliability_score": market_packet["reliability_score"],
            },
            "fundamentals": {
                "source": fundamentals_packet["source"],
                "available_at": fundamentals_packet["available_at"],
                "reliability_score": fundamentals_packet["reliability_score"],
                "restatement_risk": fundamentals_packet.get("restatement_flag", False),
            },
            "macro": {
                "source": macro_inputs["source"],
                "available_at": macro_inputs["available_at"],
                "reliability_score": macro_inputs["reliability_score"],
            },
            "shares_float": shares_float_packet,
            "sec_filings_count": len(sec_filings_packet),
            "macro_vintages_count": len(vintage_macro_packet),
            "news": [
                {
                    "source": item["source"],
                    "available_at": item["available_at"],
                    "reliability_score": item["reliability_score"],
                    "headline": item["headline"],
                }
                for item in news_items
            ],
        }
        snapshot = {
            "symbol": symbol,
            "as_of_ts": as_of_ts,
            "timestamp": datetime.fromtimestamp(as_of_ts, tz=UTC).isoformat(),
            "data_source": getattr(resolved_provider, "data_source", resolved_provider.__class__.__name__.lower()),
            "available_at": max(
                market_packet["available_at"],
                fundamentals_packet["available_at"],
                macro_inputs["available_at"],
            ),
            "ingested_at": datetime.fromtimestamp(as_of_ts, tz=UTC).isoformat(),
            "source": getattr(resolved_provider, "data_source", resolved_provider.__class__.__name__.lower()),
            "source_type": getattr(resolved_provider, "source_type", "derived"),
            "record_id": f"snapshot:{symbol}:{as_of_ts}",
            "schema_version": "2026-03-18",
            "quality_flags": quality_flags,
            "reliability_score": round(
                (
                    market_packet["reliability_score"]
                    + fundamentals_packet["reliability_score"]
                    + macro_inputs["reliability_score"]
                    + (sum(item["reliability_score"] for item in news_items) / max(1, len(news_items)))
                )
                / 4,
                4,
            ),
            "market_packet": {
                "symbol": market_packet["symbol"],
                "price": market_packet["price"],
                "closes": [row["close"] for row in price_history] or market_packet["closes"],
                "avg_volume": market_packet["avg_volume"],
                "change_pct": market_packet["change_pct"],
                "volatility": market_packet["volatility"],
                "available_at": market_packet["available_at"],
                "source": market_packet["source"],
                "source_type": market_packet["source_type"],
                "record_id": market_packet["record_id"],
                "schema_version": market_packet["schema_version"],
                "quality_flags": market_packet["quality_flags"],
                "reliability_score": market_packet["reliability_score"],
            },
            "fundamentals_packet": fundamentals_packet,
            "shares_float_packet": shares_float_packet,
            "sec_filings_packet": sec_filings_packet,
            "vintage_macro_packet": vintage_macro_packet,
            "news_packet": news_items,
            "news_inputs": [item["headline"] for item in news_items],
            "macro_inputs": macro_inputs,
            "evidence": evidence,
        }
        snapshot["snapshot_hash"] = sha256(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        snapshots[symbol] = snapshot
    return snapshots
