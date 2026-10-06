"""Tests for Root and Health Check Endpoints."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Verify that root GET / returns service identity and version."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EcoSort AI"
    assert "EcoSort AI backend is running" in data["message"]
    assert data["version"] == "1.0.0"

    # Verify security and tracing headers
    assert "x-request-id" in response.headers
    assert "x-process-time-ms" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_root_health_endpoint(client: TestClient):
    """Verify that deployment probe GET /health returns 200 healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "ecosort-ai-backend",
    }


def test_api_v1_health_endpoint(client: TestClient):
    """Verify that versioned probe GET /api/v1/health returns 200 healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ecosort-ai-backend"
