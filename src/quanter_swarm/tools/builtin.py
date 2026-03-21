"""Built-in tool implementations used by the runtime."""

from __future__ import annotations

from typing import Any

from quanter_swarm.data.base import BaseDataProvider, get_default_data_provider
from quanter_swarm.data.cache import SnapshotCache
from quanter_swarm.market.snapshot_builder import build_snapshot, build_snapshots
from quanter_swarm.tools.base import Tool
from quanter_swarm.tools.registry import ToolRegistry


class MarketDataTool(Tool):
    name = "market_data"
    timeout_seconds = 5.0

    def __init__(self, provider: BaseDataProvider | None = None, cache: SnapshotCache | None = None) -> None:
        self.provider = provider or get_default_data_provider()
        self.cache = cache

    def run(self, **kwargs: Any) -> dict[str, Any]:
        symbol = str(kwargs["symbol"]).upper()
        use_cache = bool(kwargs.get("use_cache", True))
        cache_key = symbol.upper()
        if use_cache and self.cache is not None:
            cached = self.cache.get_snapshot(cache_key)
            if cached is not None:
                cached["cache_hit"] = True
                return cached
        snapshot = build_snapshot(symbol, provider=self.provider)
        if self.cache is not None:
            self.cache.set_snapshot(cache_key, snapshot)
        return snapshot


class BatchMarketDataTool(Tool):
    name = "market_data_batch"
    timeout_seconds = 10.0

    def __init__(self, provider: BaseDataProvider | None = None, cache: SnapshotCache | None = None) -> None:
        self.provider = provider or get_default_data_provider()
        self.cache = cache

    def run(self, **kwargs: Any) -> dict[str, Any]:
        symbols = [str(item).upper() for item in kwargs.get("symbols", [])]
        use_cache = bool(kwargs.get("use_cache", True))
        snapshots: dict[str, dict[str, Any]] = {}
        pending: list[str] = []
        for symbol in symbols:
            if use_cache and self.cache is not None:
                cached = self.cache.get_snapshot(symbol)
                if cached is not None:
                    cached["cache_hit"] = True
                    snapshots[symbol] = cached
                    continue
            pending.append(symbol)
        if pending:
            fresh = build_snapshots(pending, provider=self.provider)
            snapshots.update(fresh)
            if self.cache is not None:
                for symbol, snapshot in fresh.items():
                    self.cache.set_snapshot(symbol, snapshot)
        return {symbol: snapshots[symbol] for symbol in symbols}


class MemoryCompressionTool(Tool):
    name = "memory_compression"

    def run(self, **kwargs: Any) -> dict[str, Any]:
        news = list(kwargs.get("news_inputs", []))
        return {
            "compressed": True,
            "summary": "; ".join(news[:2]),
            "payload": kwargs,
        }


class MacroEventTool(Tool):
    name = "macro_event_analysis"

    def run(self, **kwargs: Any) -> dict[str, Any]:
        macro_risk = float(kwargs.get("macro_risk", 0.0))
        direction = "negative" if macro_risk > 0.6 else "positive"
        return {"event": kwargs, "impact": direction, "confidence": round(abs(0.5 - macro_risk) + 0.5, 2)}


class SentimentAnalysisTool(Tool):
    name = "sentiment_analysis"

    def run(self, **kwargs: Any) -> dict[str, Any]:
        text = str(kwargs.get("text") or kwargs.get("compressed_context") or "")
        if not text:
            score = 0.0
        else:
            lower = text.lower()
            score = 0.5
            for token in ("stable", "momentum", "growth", "strong"):
                if token in lower:
                    score += 0.1
            for token in ("risk", "uncertainty", "weak", "decline"):
                if token in lower:
                    score -= 0.1
            score = round(max(0.0, min(1.0, score)), 2)
        return {"score": score, "text": text}


class FeatureEngineeringTool(Tool):
    name = "feature_engineering"

    def run(self, **kwargs: Any) -> dict[str, Any]:
        market = kwargs.get("market_packet", {})
        fundamentals = kwargs.get("fundamentals_packet", {})
        shares_float = kwargs.get("shares_float_packet", {})
        trend = market.get("change_pct", 0.0)
        value = 1 / (1 + fundamentals.get("valuation", 1.0))
        quality = fundamentals.get("quality", 0.0)
        avg_volume = float(market.get("avg_volume", 0.0) or 0.0)
        float_shares = float(shares_float.get("float_shares", 0.0) or 0.0)
        float_turnover = 0.0 if float_shares <= 0 else min(1.0, avg_volume / float_shares)
        crowding = 1.0 - float_turnover if float_turnover > 0 else 0.5
        return {
            "features": {
                "trend": round(trend, 4),
                "value": round(value, 4),
                "quality": round(quality, 4),
                "volatility": market.get("volatility", 0.0),
                "float_turnover": round(float_turnover, 4),
                "crowding": round(crowding, 4),
            }
        }


class RiskAssessmentTool(Tool):
    name = "risk_assessment"

    def run(self, **kwargs: Any) -> dict[str, Any]:
        warnings: list[str] = []
        volatility = float(kwargs.get("volatility", 0.0))
        macro_risk = float(kwargs.get("macro_risk", 0.0))
        if volatility > 0.06:
            warnings.append("high_volatility")
        if macro_risk >= 0.8:
            warnings.append("elevated_macro_risk")
        return {
            "approved": not warnings,
            "warnings": warnings,
            "proposal": kwargs,
        }


def build_default_tool_registry(
    *,
    provider: BaseDataProvider | None = None,
    cache: SnapshotCache | None = None,
    allowed_tools: list[str] | None = None,
) -> ToolRegistry:
    registry = ToolRegistry()
    allowlist = set(allowed_tools or [])
    for tool in (
        MarketDataTool(provider=provider, cache=cache),
        BatchMarketDataTool(provider=provider, cache=cache),
        MemoryCompressionTool(),
        MacroEventTool(),
        SentimentAnalysisTool(),
        FeatureEngineeringTool(),
        RiskAssessmentTool(),
    ):
        if allowlist and tool.name not in allowlist:
            continue
        registry.register(tool)
    return registry
