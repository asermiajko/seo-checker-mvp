"""Integration tests for POST /api/check endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_api_check_happy_path(client: TestClient) -> None:
    """Test POST /api/check with valid URL returns full report.

    This is the happy path test:
    - Valid site_url and telegram_id
    - All checks pass successfully
    - Returns 200 OK with full report structure
    """
    # Arrange
    request_data = {
        "site_url": "https://example.ru",
        "telegram_id": 123456789,
    }

    # Mock HTTP client to avoid real network calls
    mock_client = AsyncMock()

    # Mock robots.txt response
    mock_client.get.return_value = AsyncMock(
        status_code=200,
        text=(
            "User-agent: *\nDisallow: /admin\n"
            "Sitemap: https://example.ru/sitemap.xml"
        ),
    )

    # Act
    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json=request_data)

    # Assert
    assert response.status_code == 200

    data = response.json()

    # Check top-level structure
    assert "score" in data
    assert "problems_critical" in data
    assert "problems_important" in data
    assert "checks_ok" in data
    assert "categories" in data
    assert "top_priorities" in data
    assert "detailed_checks" in data
    assert "metadata" in data

    # Validate score
    assert isinstance(data["score"], (int, float))  # noqa: UP038
    assert 0.0 <= data["score"] <= 10.0

    # Validate counts
    assert isinstance(data["problems_critical"], int)
    assert isinstance(data["problems_important"], int)
    assert isinstance(data["checks_ok"], int)
    assert data["problems_critical"] >= 0
    assert data["problems_important"] >= 0
    assert data["checks_ok"] >= 0

    # Validate categories
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) > 0

    for category in data["categories"]:
        assert "name" in category
        assert "score" in category
        assert "total" in category
        assert "checks" in category
        assert isinstance(category["checks"], list)

    # Validate top_priorities
    assert isinstance(data["top_priorities"], list)
    assert len(data["top_priorities"]) <= 3

    for priority in data["top_priorities"]:
        assert "severity" in priority
        assert priority["severity"] in ("critical", "important", "enhancement")
        assert "title" in priority
        assert "message" in priority or "action" in priority
        assert "check_id" in priority

    # Validate detailed_checks
    assert isinstance(data["detailed_checks"], list)
    assert len(data["detailed_checks"]) >= 6

    for check in data["detailed_checks"]:
        assert "id" in check
        assert "name" in check
        assert "status" in check
        assert check["status"] in ("ok", "partial", "problem", "error")
        assert "message" in check
        assert "category" in check
        assert check["category"] in (
            "technical",
            "content",
            "structure",
            "seo",
            "social",
        )

        # If status is not ok, should have severity
        if check["status"] in ("problem", "partial"):
            assert "severity" in check or check["status"] == "error"

    # Validate metadata
    assert "checked_at" in data["metadata"]
    assert "processing_time_sec" in data["metadata"]
    assert "checks_total" in data["metadata"]
    assert "checks_completed" in data["metadata"]
    assert "checks_failed" in data["metadata"]

    assert isinstance(data["metadata"]["processing_time_sec"], (int, float))  # noqa: UP038
    assert data["metadata"]["processing_time_sec"] >= 0
    assert data["metadata"]["checks_total"] >= 6
    assert data["metadata"]["checks_completed"] >= 0
    assert data["metadata"]["checks_failed"] >= 0


@pytest.mark.asyncio
async def test_api_check_validates_site_url(client: TestClient) -> None:
    """Test that invalid site_url returns 422 validation error."""
    # Arrange
    invalid_requests = [
        {"site_url": "not-a-url", "telegram_id": 123456789},
        {"site_url": "ftp://example.ru", "telegram_id": 123456789},
        {"site_url": "http://localhost/test", "telegram_id": 123456789},
        {"site_url": "http://127.0.0.1", "telegram_id": 123456789},
        {"site_url": "", "telegram_id": 123456789},
    ]

    for request_data in invalid_requests:
        # Act
        response = client.post("/api/check", json=request_data)

        # Assert
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data  # FastAPI returns "detail" for validation errors


@pytest.mark.asyncio
async def test_api_check_validates_telegram_id(client: TestClient) -> None:
    """Test that invalid telegram_id returns 400 validation error."""
    # Arrange
    invalid_requests = [
        {"site_url": "https://example.ru", "telegram_id": -1},
        {"site_url": "https://example.ru", "telegram_id": 0},
        {"site_url": "https://example.ru", "telegram_id": "not-a-number"},
    ]

    for request_data in invalid_requests:
        # Act
        response = client.post("/api/check", json=request_data)

        # Assert
        assert response.status_code in (400, 422)  # 422 is Pydantic validation error
        data = response.json()
        assert "error" in data or "detail" in data  # FastAPI uses "detail" for validation


@pytest.mark.asyncio
async def test_api_check_saves_to_database(client: TestClient) -> None:
    """Test that successful check saves CheckRequest and CheckResult to database."""
    # Arrange
    request_data = {
        "site_url": "https://example.ru",
        "telegram_id": 987654321,
    }

    # Mock HTTP client
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200,
        text="User-agent: *\nSitemap: https://example.ru/sitemap.xml",
    )

    # Act
    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json=request_data)

    # Assert
    assert response.status_code == 200

    # TODO: Query database to verify CheckRequest and CheckResult were saved
    # This will be implemented when database integration is ready
