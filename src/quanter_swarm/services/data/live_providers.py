"""HTTP-backed market, filings, fundamentals, and macro providers."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree

import httpx

from quanter_swarm.errors import DataProviderError
from quanter_swarm.services.data.base import BaseDataProvider


def _iso_from_epoch_ms(value: int | float | str | None) -> str | None:
    if value is None:
        return None
    numeric = float(value)
    if numeric > 10_000_000_000:
        numeric /= 1000
    return datetime.fromtimestamp(numeric, tz=UTC).isoformat()


def _iso_from_date(value: str | None) -> str | None:
    if not value:
        return None
    if "T" in value:
        return value.replace("Z", "+00:00")
    return f"{value}T00:00:00+00:00"


@dataclass(slots=True)
class HttpProviderMixin:
    base_url: str
    timeout: float = 15.0
    headers: dict[str, str] | None = None
    client: httpx.Client | None = None
    _client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = self.client or httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        )

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        response = self._client.get(path, params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DataProviderError(f"{self.__class__.__name__} request failed for {path}: {exc}") from exc
        content_type = response.headers.get("content-type", "")
        if "json" in content_type:
            return response.json()
        return response.text


class PolygonMarketDataProvider(BaseDataProvider, HttpProviderMixin):
    data_source = "polygon"
    source_type = "commercial"

    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            raise DataProviderError("PolygonMarketDataProvider requires POLYGON_API_KEY.")
        HttpProviderMixin.__init__(
            self,
            base_url="https://api.polygon.io",
            client=client,
        )
        self.__post_init__()

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        payload = self._get(
            f"/v2/aggs/ticker/{symbol.upper()}/prev",
            params={"adjusted": "true", "apiKey": self.api_key},
        )
        results = payload.get("results", [])
        return [
            {
                "symbol": symbol.upper(),
                "open": row.get("o"),
                "high": row.get("h"),
                "low": row.get("l"),
                "close": row.get("c"),
                "volume": row.get("v"),
                "ts_event": _iso_from_epoch_ms(row.get("t")),
                "ts_available": _iso_from_epoch_ms(row.get("t")),
                "source": self.data_source,
            }
            for row in results[-lookback:]
        ]

    def get_latest_prices(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_latest_price(symbol) for symbol in symbols}

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        snapshot = self._get(f"/v2/snapshot/locale/us/markets/stocks/tickers/{symbol.upper()}", params={"apiKey": self.api_key})
        ticker = snapshot.get("ticker", {})
        day = ticker.get("day", {})
        prev_day = ticker.get("prevDay", {})
        min_row = ticker.get("min", {})
        updated = _iso_from_epoch_ms(ticker.get("updated"))
        return {
            "symbol": symbol.upper(),
            "price": day.get("c") or min_row.get("c") or prev_day.get("c"),
            "previous_close": prev_day.get("c"),
            "avg_volume": ticker.get("todaysChangePerc", 0.0),
            "change_pct": round(float(ticker.get("todaysChangePerc", 0.0)) / 100, 4),
            "volatility": abs(round(float(ticker.get("todaysChangePerc", 0.0)) / 100, 4)),
            "closes": [prev_day.get("c"), day.get("c")],
            "ts_event": updated,
            "ts_available": updated,
            "vendor_symbol": symbol.upper(),
            "latency_ms": 0,
            "quality_flags": ["commercial_source"],
        }

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        payload = self._get("/v2/reference/news", params={"ticker": symbol.upper(), "limit": limit, "apiKey": self.api_key})
        rows = payload.get("results", [])
        return [
            {
                "symbol": symbol.upper(),
                "headline": row.get("title", ""),
                "body": row.get("description", ""),
                "published_at": row.get("published_utc"),
                "ingested_at": datetime.now(tz=UTC).isoformat(),
                "source": self.data_source,
                "publisher": (row.get("publisher") or {}).get("name", "polygon"),
                "url": row.get("article_url"),
                "language": row.get("language", "en"),
                "event_type": "company_update",
                "event_direction": "neutral",
                "event_confidence": 0.7,
                "quality_flags": ["commercial_source"],
            }
            for row in rows
        ]


class FmpMarketDataProvider(BaseDataProvider, HttpProviderMixin):
    data_source = "fmp"
    source_type = "commercial"

    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise DataProviderError("FmpMarketDataProvider requires FMP_API_KEY.")
        HttpProviderMixin.__init__(self, base_url="https://financialmodelingprep.com/api", client=client)
        self.__post_init__()

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        payload = self._get(
            f"/v3/historical-price-full/{symbol.upper()}",
            params={"timeseries": lookback, "apikey": self.api_key},
        )
        return [
            {
                "symbol": symbol.upper(),
                "open": row.get("open"),
                "high": row.get("high"),
                "low": row.get("low"),
                "close": row.get("close"),
                "volume": row.get("volume"),
                "ts_event": _iso_from_date(row.get("date")),
                "ts_available": _iso_from_date(row.get("date")),
                "source": self.data_source,
            }
            for row in reversed(payload.get("historical", [])[-lookback:])
        ]

    def get_latest_prices(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        joined = ",".join(symbol.upper() for symbol in symbols)
        payload = self._get(f"/v3/quote/{joined}", params={"apikey": self.api_key})
        rows: dict[str, dict[str, Any]] = {}
        normalized = [symbol.upper() for symbol in symbols]
        for index, row in enumerate(payload):
            symbol = str(row.get("symbol") or normalized[min(index, len(normalized) - 1)]).upper()
            rows[symbol] = {
                "symbol": symbol,
                "price": row.get("price"),
                "previous_close": row.get("previousClose"),
                "avg_volume": row.get("avgVolume"),
                "change_pct": round(float(row.get("changesPercentage", 0.0)) / 100, 4),
                "volatility": abs(round(float(row.get("changesPercentage", 0.0)) / 100, 4)),
                "closes": [row.get("previousClose"), row.get("price")],
                "ts_event": _iso_from_date(row.get("timestamp")) or datetime.now(tz=UTC).isoformat(),
                "ts_available": datetime.now(tz=UTC).isoformat(),
                "vendor_symbol": symbol,
                "latency_ms": 0,
                "quality_flags": ["commercial_source"],
            }
        return rows

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        payload = self._get(f"/v3/quote/{symbol.upper()}", params={"apikey": self.api_key})
        row = payload[0]
        return {
            "symbol": symbol.upper(),
            "price": row.get("price"),
            "previous_close": row.get("previousClose"),
            "avg_volume": row.get("avgVolume"),
            "change_pct": round(float(row.get("changesPercentage", 0.0)) / 100, 4),
            "volatility": abs(round(float(row.get("changesPercentage", 0.0)) / 100, 4)),
            "closes": [row.get("previousClose"), row.get("price")],
            "ts_event": _iso_from_date(row.get("timestamp")) or datetime.now(tz=UTC).isoformat(),
            "ts_available": datetime.now(tz=UTC).isoformat(),
            "vendor_symbol": symbol.upper(),
            "latency_ms": 0,
            "quality_flags": ["commercial_source"],
        }

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        payload = self._get("/v3/stock_news", params={"tickers": symbol.upper(), "limit": limit, "apikey": self.api_key})
        return [
            {
                "symbol": symbol.upper(),
                "headline": row.get("title", ""),
                "body": row.get("text", ""),
                "published_at": row.get("publishedDate"),
                "ingested_at": datetime.now(tz=UTC).isoformat(),
                "source": self.data_source,
                "publisher": row.get("site", "fmp"),
                "url": row.get("url"),
                "language": "en",
                "event_type": "company_update",
                "event_direction": "neutral",
                "event_confidence": 0.65,
                "quality_flags": ["commercial_source"],
            }
            for row in payload
        ]


class FmpSharesFloatProvider(HttpProviderMixin):
    source = "fmp_shares_float"
    source_type = "commercial"

    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise DataProviderError("FmpSharesFloatProvider requires FMP_API_KEY.")
        HttpProviderMixin.__init__(self, base_url="https://financialmodelingprep.com/api", client=client)
        self.__post_init__()

    def get_shares_float(self, symbol: str) -> dict[str, Any]:
        payload = self._get("/v4/shares_float", params={"symbol": symbol.upper(), "apikey": self.api_key})
        row = payload[0]
        return {
            "symbol": symbol.upper(),
            "date": row.get("date"),
            "free_float": row.get("freeFloat"),
            "float_shares": row.get("floatShares"),
            "outstanding_shares": row.get("outstandingShares"),
            "source": self.source,
            "source_type": self.source_type,
            "available_at": _iso_from_date(row.get("date")),
        }

    def get_shares_float_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_shares_float(symbol) for symbol in symbols}


class SecFilingsProvider(HttpProviderMixin):
    source = "sec_edgar"
    source_type = "official"

    def __init__(self, user_agent: str | None = None, client: httpx.Client | None = None) -> None:
        agent = str(user_agent or os.getenv("SEC_USER_AGENT", "QuanterSwarm research@example.com"))
        HttpProviderMixin.__init__(
            self,
            base_url="https://data.sec.gov",
            client=client,
            headers={"User-Agent": agent, "Accept-Encoding": "gzip, deflate"},
        )
        self.__post_init__()

    def _resolve_cik(self, ticker: str) -> str:
        payload = self._get("/files/company_tickers.json")
        for row in payload.values():
            if str(row.get("ticker", "")).upper() == ticker.upper():
                return str(row["cik_str"]).zfill(10)
        raise DataProviderError(f"Unable to resolve CIK for ticker '{ticker}'.")

    def get_filings(self, ticker: str, forms: tuple[str, ...] = ("10-K", "10-Q", "8-K"), limit: int = 10) -> list[dict[str, Any]]:
        cik = self._resolve_cik(ticker)
        payload = self._get(f"/submissions/CIK{cik}.json")
        recent = payload.get("filings", {}).get("recent", {})
        rows = []
        total = len(recent.get("form", []))
        for index in range(total):
            form = recent["form"][index]
            if forms and form not in forms:
                continue
            accession = recent["accessionNumber"][index].replace("-", "")
            primary_document = recent["primaryDocument"][index]
            accepted_at = _iso_from_date(recent.get("filingDate", [None])[index])
            rows.append(
                {
                    "entity_id": cik,
                    "ticker": ticker.upper(),
                    "form": form,
                    "filed_at": accepted_at,
                    "accepted_at": accepted_at,
                    "available_at": accepted_at,
                    "source_doc": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_document}",
                    "source": self.source,
                    "restatement_flag": False,
                }
            )
            if len(rows) >= limit:
                break
        return rows

    def get_filings_batch(
        self,
        tickers: list[str],
        forms: tuple[str, ...] = ("10-K", "10-Q", "8-K"),
        limit: int = 10,
    ) -> dict[str, list[dict[str, Any]]]:
        return {ticker.upper(): self.get_filings(ticker, forms=forms, limit=limit) for ticker in tickers}


class SecXbrlFactsProvider(HttpProviderMixin):
    source = "sec_xbrl_facts"
    source_type = "official"

    def __init__(self, user_agent: str | None = None, client: httpx.Client | None = None) -> None:
        agent = str(user_agent or os.getenv("SEC_USER_AGENT", "QuanterSwarm research@example.com"))
        HttpProviderMixin.__init__(
            self,
            base_url="https://data.sec.gov",
            client=client,
            headers={"User-Agent": agent, "Accept-Encoding": "gzip, deflate"},
        )
        self.__post_init__()
        self._filings_provider = SecFilingsProvider(user_agent=agent, client=self._client)

    def get_facts(self, ticker: str, concepts: tuple[str, ...] = ("Revenues", "NetIncomeLoss")) -> list[dict[str, Any]]:
        cik = self._filings_provider._resolve_cik(ticker)
        payload = self._get(f"/api/xbrl/companyfacts/CIK{cik}.json")
        rows: list[dict[str, Any]] = []
        us_gaap = payload.get("facts", {}).get("us-gaap", {})
        for concept in concepts:
            fact = us_gaap.get(concept)
            if not fact:
                continue
            units = fact.get("units", {})
            for unit, observations in units.items():
                for observation in observations[-5:]:
                    rows.append(
                        {
                            "entity_id": cik,
                            "ticker": ticker.upper(),
                            "fiscal_period": observation.get("fp"),
                            "period_end": _iso_from_date(observation.get("end")),
                            "filed_at": _iso_from_date(observation.get("filed")),
                            "accepted_at": _iso_from_date(observation.get("filed")),
                            "available_at": _iso_from_date(observation.get("filed")),
                            "metric_name": concept,
                            "metric_value": observation.get("val"),
                            "unit": unit,
                            "source_doc": observation.get("accn"),
                            "source": self.source,
                            "restatement_flag": bool(observation.get("frame")),
                        }
                    )
        return rows

    def get_facts_batch(
        self,
        tickers: list[str],
        concepts: tuple[str, ...] = ("Revenues", "NetIncomeLoss"),
    ) -> dict[str, list[dict[str, Any]]]:
        return {ticker.upper(): self.get_facts(ticker, concepts=concepts) for ticker in tickers}


class CompanyIRProvider(HttpProviderMixin):
    source = "company_ir"
    source_type = "official"

    def __init__(self, client: httpx.Client | None = None) -> None:
        HttpProviderMixin.__init__(self, base_url="https://example.com", client=client)
        self.__post_init__()

    def get_releases(self, rss_url: str, limit: int = 10) -> list[dict[str, Any]]:
        payload = self._get(rss_url)
        root = ElementTree.fromstring(payload)
        rows = []
        for item in root.findall(".//item")[:limit]:
            pub_date = item.findtext("pubDate")
            published_at = (
                parsedate_to_datetime(pub_date).astimezone(UTC).isoformat()
                if pub_date
                else datetime.now(tz=UTC).isoformat()
            )
            rows.append(
                {
                    "headline": item.findtext("title", default=""),
                    "body": item.findtext("description", default=""),
                    "published_at": published_at,
                    "ingested_at": datetime.now(tz=UTC).isoformat(),
                    "source": self.source,
                    "publisher": item.findtext("source", default="company_ir"),
                    "url": item.findtext("link", default=""),
                    "language": "en",
                    "quality_flags": ["issuer_published"],
                }
            )
        return rows


class FredMacroProvider(HttpProviderMixin):
    source = "fred"
    source_type = "official"

    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise DataProviderError("FredMacroProvider requires FRED_API_KEY.")
        HttpProviderMixin.__init__(self, base_url="https://api.stlouisfed.org", client=client)
        self.__post_init__()

    def get_series(self, series_id: str, start_date: str | None = None, end_date: str | None = None) -> list[dict[str, Any]]:
        payload = self._get(
            "/fred/series/observations",
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start_date,
                "observation_end": end_date,
            },
        )
        return [
            {
                "series_id": series_id,
                "observation_date": row.get("date"),
                "value": row.get("value"),
                "available_at": _iso_from_date(row.get("date")),
                "source": self.source,
            }
            for row in payload.get("observations", [])
        ]

    def get_series_batch(
        self,
        series_ids: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        return {series_id: self.get_series(series_id, start_date=start_date, end_date=end_date) for series_id in series_ids}


class AlfredVintageMacroProvider(HttpProviderMixin):
    source = "alfred"
    source_type = "official"

    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise DataProviderError("AlfredVintageMacroProvider requires FRED_API_KEY.")
        HttpProviderMixin.__init__(self, base_url="https://api.stlouisfed.org", client=client)
        self.__post_init__()

    def get_series_vintages(
        self,
        series_id: str,
        realtime_start: str | None = None,
        realtime_end: str | None = None,
    ) -> list[dict[str, Any]]:
        payload = self._get(
            "/fred/series/observations",
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "realtime_start": realtime_start,
                "realtime_end": realtime_end,
                "output_type": 2,
            },
        )
        return [
            {
                "series_id": series_id,
                "observation_date": row.get("date"),
                "release_time": _iso_from_date(row.get("realtime_start")),
                "available_at": _iso_from_date(row.get("realtime_start")),
                "value": row.get("value"),
                "vintage_date": row.get("realtime_start"),
                "source": self.source,
            }
            for row in payload.get("observations", [])
        ]

    def get_series_vintages_batch(
        self,
        series_ids: list[str],
        realtime_start: str | None = None,
        realtime_end: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            series_id: self.get_series_vintages(series_id, realtime_start=realtime_start, realtime_end=realtime_end)
            for series_id in series_ids
        }


class CompositeMarketDataProvider(BaseDataProvider):
    """Compose market and auxiliary providers under one contract."""

    data_source = "composite"
    source_type = "derived"

    def __init__(
        self,
        *,
        market_provider: BaseDataProvider,
        filings_provider: SecFilingsProvider | None = None,
        xbrl_provider: SecXbrlFactsProvider | None = None,
        shares_float_provider: FmpSharesFloatProvider | None = None,
        macro_provider: FredMacroProvider | None = None,
        vintage_macro_provider: AlfredVintageMacroProvider | None = None,
    ) -> None:
        self.market_provider = market_provider
        self.filings_provider = filings_provider
        self.xbrl_provider = xbrl_provider
        self.shares_float_provider = shares_float_provider
        self.macro_provider = macro_provider
        self.vintage_macro_provider = vintage_macro_provider
        self.data_source = getattr(market_provider, "data_source", "composite")
        self.source_type = getattr(market_provider, "source_type", "derived")

    def get_price_history(self, symbol: str, lookback: int = 5) -> list[dict[str, Any]]:
        return self.market_provider.get_price_history(symbol, lookback=lookback)

    def get_price_histories(self, symbols: list[str], lookback: int = 5) -> dict[str, list[dict[str, Any]]]:
        return self.market_provider.get_price_histories(symbols, lookback=lookback)

    def get_latest_price(self, symbol: str) -> dict[str, Any]:
        return self.market_provider.get_latest_price(symbol)

    def get_latest_prices(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return self.market_provider.get_latest_prices(symbols)

    def get_news(self, symbol: str, limit: int = 5) -> list[dict[str, Any]]:
        return self.market_provider.get_news(symbol, limit=limit)

    def get_news_batch(self, symbols: list[str], limit: int = 5) -> dict[str, list[dict[str, Any]]]:
        return self.market_provider.get_news_batch(symbols, limit=limit)

    def get_fundamentals(self, symbol: str) -> dict[str, Any]:
        payload = self.market_provider.get_fundamentals(symbol)
        payload["xbrl_facts"] = self.get_xbrl_facts(symbol)
        payload["sec_filings"] = self.get_filings(symbol)
        return payload

    def get_fundamentals_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_fundamentals(symbol) for symbol in symbols}

    def get_macro(self, symbol: str) -> dict[str, Any]:
        if self.macro_provider is None:
            return self.market_provider.get_macro(symbol)
        rows = self.macro_provider.get_series("DFF")
        latest = rows[-1] if rows else {}
        value = latest.get("value")
        numeric_value = 0.0 if value in {None, "."} else float(str(value))
        return {
            "macro_risk": min(1.0, max(0.0, numeric_value / 10)),
            "macro_theme": "rates_high" if numeric_value > 3 else "disinflation",
            "observation_date": latest.get("observation_date"),
            "release_time": latest.get("available_at"),
            "available_at": latest.get("available_at"),
            "source": getattr(self.macro_provider, "source", "fred"),
            "series_id": latest.get("series_id", "DFF"),
            "value": value,
        }

    def get_macro_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        return {symbol.upper(): self.get_macro(symbol) for symbol in symbols}

    def get_shares_float(self, symbol: str) -> dict[str, Any]:
        if self.shares_float_provider is None:
            return {}
        return self.shares_float_provider.get_shares_float(symbol)

    def get_shares_float_batch(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        if self.shares_float_provider is None:
            return {symbol.upper(): {} for symbol in symbols}
        return self.shares_float_provider.get_shares_float_batch(symbols)

    def get_filings(self, symbol: str, limit: int = 10) -> list[dict[str, Any]]:
        if self.filings_provider is None:
            return []
        return self.filings_provider.get_filings(symbol, limit=limit)

    def get_filings_batch(self, symbols: list[str], limit: int = 10) -> dict[str, list[dict[str, Any]]]:
        if self.filings_provider is None:
            return {symbol.upper(): [] for symbol in symbols}
        return self.filings_provider.get_filings_batch(symbols, limit=limit)

    def get_xbrl_facts(self, symbol: str) -> list[dict[str, Any]]:
        if self.xbrl_provider is None:
            return []
        return self.xbrl_provider.get_facts(symbol)

    def get_xbrl_facts_batch(self, symbols: list[str]) -> dict[str, list[dict[str, Any]]]:
        if self.xbrl_provider is None:
            return {symbol.upper(): [] for symbol in symbols}
        return self.xbrl_provider.get_facts_batch(symbols)

    def get_macro_vintages(self, symbol: str) -> list[dict[str, Any]]:
        if self.vintage_macro_provider is None:
            return []
        return self.vintage_macro_provider.get_series_vintages("DFF")

    def get_macro_vintages_batch(self, symbols: list[str]) -> dict[str, list[dict[str, Any]]]:
        if self.vintage_macro_provider is None:
            return {symbol.upper(): [] for symbol in symbols}
        vintages = self.vintage_macro_provider.get_series_vintages_batch(["DFF"]).get("DFF", [])
        return {symbol.upper(): list(vintages) for symbol in symbols}
