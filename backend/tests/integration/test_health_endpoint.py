"""Integration tests for health endpoint."""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """Test GET /api/health returns status."""
    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "status" in data
    assert data["status"] in ("ok", "degraded")
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"] in ("ok", "error")


def test_health_endpoint_database_check(client: TestClient) -> None:
    """Test that health endpoint actually checks database connection."""
    # Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Database check should be performed (in test env, SQLite should be OK)
    assert data["checks"]["database"] == "ok"
    assert data["status"] == "ok"
