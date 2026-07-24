"""Teste do endpoint /health da API FastAPI."""

from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AI CSV Query API"
    assert "timestamp" in data
