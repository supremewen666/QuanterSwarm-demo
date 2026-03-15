from fastapi.testclient import TestClient

from quanter_swarm.api.app import app


def test_research_endpoint_returns_structured_payload() -> None:
    client = TestClient(app)
    response = client.post("/research", json={"symbol": "AAPL"})
    assert response.status_code == 200
    body = response.json()
    assert body["active_regime"]
    assert "portfolio_suggestion" in body
