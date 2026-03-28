from fastapi.testclient import TestClient

from quanter_swarm.adapters import api_app


def test_research_endpoint_returns_structured_payload() -> None:
    client = TestClient(api_app)
    response = client.post("/research", json={"symbol": "AAPL"})
    assert response.status_code == 200
    body = response.json()
    assert body["active_regime"]
    assert body["regime"] == body["active_regime"]
    assert "portfolio_suggestion" in body
    assert body["provider_summary"]["provider"] == "deterministic"
    assert body["architecture_summary"]["control_plane"]["flow"] == [
        "orchestrator",
        "router",
        "leader",
        "specialist",
    ]


def test_batch_research_endpoint_returns_multiple_results() -> None:
    client = TestClient(api_app)
    response = client.post("/research/batch", json={"symbols": ["AAPL", "MSFT"]})
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2


def test_batch_data_endpoints_return_payloads() -> None:
    client = TestClient(api_app)
    fundamentals = client.post("/data/fundamentals/batch", json={"symbols": ["AAPL", "MSFT"]})
    assert fundamentals.status_code == 200
    assert set(fundamentals.json()["results"]) == {"AAPL", "MSFT"}

    macro = client.post("/data/macro/batch", json={"symbols": ["AAPL", "MSFT"]})
    assert macro.status_code == 200
    assert set(macro.json()["results"]) == {"AAPL", "MSFT"}


def test_provider_catalog_endpoint_returns_configured_topology() -> None:
    client = TestClient(api_app)
    response = client.get("/data/providers")
    assert response.status_code == 200
    body = response.json()
    assert "available" in body
    assert body["configured"]["provider"] == "deterministic"


def test_research_endpoint_requires_symbol_or_symbols() -> None:
    client = TestClient(api_app)
    response = client.post("/research", json={})
    assert response.status_code == 422
