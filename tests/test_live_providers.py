import httpx

from quanter_swarm.services.data import (
    AlfredVintageMacroProvider,
    FmpMarketDataProvider,
    FmpSharesFloatProvider,
    FredMacroProvider,
    PolygonMarketDataProvider,
    SecFilingsProvider,
    SecXbrlFactsProvider,
    available_providers,
    create_provider,
)


def test_provider_registry_exposes_live_integrations() -> None:
    names = available_providers()
    assert "polygon_market_data" in names
    assert "sec_xbrl_facts" in names
    assert create_provider("fred_macro", api_key="demo", client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"observations": []})))) is not None


def test_polygon_market_data_provider_parses_snapshot_and_news() -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/snapshot/locale/us/markets/stocks/tickers/AAPL"):
            return httpx.Response(
                200,
                json={
                    "ticker": {
                        "updated": 1_773_000_000_000,
                        "day": {"c": 101.2},
                        "prevDay": {"c": 99.8},
                        "todaysChangePerc": 1.4,
                    }
                },
            )
        if request.url.path.endswith("/reference/news"):
            return httpx.Response(
                200,
                json={"results": [{"title": "AAPL update", "description": "desc", "published_utc": "2026-03-18T09:30:00+00:00", "article_url": "https://example.com", "publisher": {"name": "Polygon"}}]},
            )
        return httpx.Response(200, json={"results": [{"o": 100, "h": 102, "l": 99, "c": 101, "v": 123, "t": 1_773_000_000_000}]})

    provider = PolygonMarketDataProvider(api_key="demo", client=httpx.Client(transport=httpx.MockTransport(_handler), base_url="https://api.polygon.io"))
    assert provider.get_latest_price("AAPL")["price"] == 101.2
    assert provider.get_latest_prices(["AAPL"])["AAPL"]["price"] == 101.2
    assert provider.get_news("AAPL")[0]["publisher"] == "Polygon"


def test_fmp_and_macro_providers_parse_payloads() -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        if "quote" in request.url.path:
            return httpx.Response(200, json=[{"price": 201.5, "previousClose": 199.5, "avgVolume": 1000, "changesPercentage": 1.0, "timestamp": "2026-03-18"}])
        if "shares_float" in request.url.path:
            return httpx.Response(200, json=[{"symbol": "MSFT", "date": "2026-03-18", "freeFloat": 0.9, "floatShares": 100, "outstandingShares": 110}])
        if "stock_news" in request.url.path:
            return httpx.Response(200, json=[{"title": "MSFT update", "text": "body", "publishedDate": "2026-03-18T09:30:00+00:00", "site": "FMP", "url": "https://example.com"}])
        if "historical-price-full" in request.url.path:
            return httpx.Response(200, json={"historical": [{"date": "2026-03-18", "open": 200, "high": 202, "low": 198, "close": 201, "volume": 1000}]})
        return httpx.Response(200, json={"observations": [{"date": "2026-03-18", "value": "4.25", "realtime_start": "2026-03-19"}]})

    client = httpx.Client(transport=httpx.MockTransport(_handler), base_url="https://financialmodelingprep.com/api")
    fmp = FmpMarketDataProvider(api_key="demo", client=client)
    assert fmp.get_latest_price("MSFT")["price"] == 201.5
    assert fmp.get_latest_prices(["MSFT"])["MSFT"]["price"] == 201.5
    assert fmp.get_price_history("MSFT")[0]["close"] == 201
    assert fmp.get_news("MSFT")[0]["publisher"] == "FMP"

    float_provider = FmpSharesFloatProvider(api_key="demo", client=client)
    assert float_provider.get_shares_float("MSFT")["float_shares"] == 100
    assert float_provider.get_shares_float_batch(["MSFT"])["MSFT"]["float_shares"] == 100

    fred_client = httpx.Client(transport=httpx.MockTransport(_handler), base_url="https://api.stlouisfed.org")
    fred = FredMacroProvider(api_key="demo", client=fred_client)
    alfred = AlfredVintageMacroProvider(api_key="demo", client=fred_client)
    assert fred.get_series("DFF")[0]["value"] == "4.25"
    assert fred.get_series_batch(["DFF"])["DFF"][0]["value"] == "4.25"
    assert alfred.get_series_vintages("DFF")[0]["vintage_date"] == "2026-03-19"
    assert alfred.get_series_vintages_batch(["DFF"])["DFF"][0]["vintage_date"] == "2026-03-19"


def test_sec_providers_parse_filings_and_facts() -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/files/company_tickers.json"):
            return httpx.Response(200, json={"0": {"ticker": "AAPL", "cik_str": 320193}})
        if request.url.path.endswith("/submissions/CIK0000320193.json"):
            return httpx.Response(
                200,
                json={
                    "filings": {
                        "recent": {
                            "form": ["10-K"],
                            "accessionNumber": ["0000320193-24-000123"],
                            "primaryDocument": ["aapl10k.htm"],
                            "filingDate": ["2026-02-01"],
                        }
                    }
                },
            )
        return httpx.Response(
            200,
            json={
                "facts": {
                    "us-gaap": {
                        "Revenues": {
                            "units": {
                                "USD": [
                                    {"fp": "FY", "end": "2025-12-31", "filed": "2026-02-01", "val": 1000, "accn": "0000320193-24-000123"}
                                ]
                            }
                        }
                    }
                }
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(_handler), base_url="https://data.sec.gov")
    filings = SecFilingsProvider(client=client)
    facts = SecXbrlFactsProvider(client=client)
    assert filings.get_filings("AAPL")[0]["ticker"] == "AAPL"
    assert filings.get_filings_batch(["AAPL"])["AAPL"][0]["ticker"] == "AAPL"
    assert facts.get_facts("AAPL")[0]["metric_name"] == "Revenues"
    assert facts.get_facts_batch(["AAPL"])["AAPL"][0]["metric_name"] == "Revenues"
