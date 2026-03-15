from fastapi.testclient import TestClient

from quanter_swarm.api.app import app


def test_research_endpoint_returns_structured_payload() -> None:
    client = TestClient(app)
    response = client.post("/research", json={"symbol": "AAPL"})
    assert response.status_code == 200
    body = response.json()
    assert body["active_regime"]
    assert body["regime"] == body["active_regime"]
    assert "portfolio_suggestion" in body


def test_batch_research_endpoint_returns_multiple_results() -> None:
    client = TestClient(app)
    response = client.post("/research/batch", json={"symbols": ["AAPL", "MSFT"]})
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2


def test_research_endpoint_requires_symbol_or_symbols() -> None:
    client = TestClient(app)
    response = client.post("/research", json={})
    assert response.status_code == 422
