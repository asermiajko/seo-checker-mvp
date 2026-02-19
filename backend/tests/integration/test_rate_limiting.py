"""Integration tests for rate limiting."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_rate_limit_allows_5_requests(client: TestClient) -> None:
    """Test that rate limit allows 5 requests per hour."""
    # Arrange
    telegram_id = 111111111
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200,
        text="User-agent: *\nSitemap: https://example.ru/sitemap.xml",
    )

    # Act - Make 5 requests
    with patch("httpx.AsyncClient", return_value=mock_client):
        for i in range(5):
            request_data = {
                "site_url": f"https://example{i}.ru",
                "telegram_id": telegram_id,
            }
            response = client.post("/api/check", json=request_data)

            # Assert - All 5 should succeed
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_blocks_6th_request(client: TestClient) -> None:
    """Test that 6th request within hour returns 429."""
    # Arrange
    telegram_id = 222222222
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200,
        text="User-agent: *\nSitemap: https://example.ru/sitemap.xml",
    )

    # Act - Make 5 successful requests
    with patch("httpx.AsyncClient", return_value=mock_client):
        for i in range(5):
            request_data = {
                "site_url": f"https://example{i}.ru",
                "telegram_id": telegram_id,
            }
            response = client.post("/api/check", json=request_data)
            assert response.status_code == 200

        # 6th request should be blocked
        response = client.post(
            "/api/check",
            json={"site_url": "https://example6.ru", "telegram_id": telegram_id},
        )

    # Assert
    assert response.status_code == 429
    data = response.json()

    # Check error structure
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"]["code"] == "rate_limit_exceeded"
    assert "retry_after_sec" in data["detail"]["error"]
    assert data["detail"]["error"]["retry_after_sec"] == 3600


@pytest.mark.asyncio
async def test_rate_limit_per_user(client: TestClient) -> None:
    """Test that rate limit is per telegram_id (different users isolated)."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200,
        text="User-agent: *\nSitemap: https://example.ru/sitemap.xml",
    )

    # Act - User 1 makes 5 requests
    with patch("httpx.AsyncClient", return_value=mock_client):
        for i in range(5):
            response = client.post(
                "/api/check",
                json={"site_url": f"https://example{i}.ru", "telegram_id": 333333333},
            )
            assert response.status_code == 200

        # User 2 should still be able to make requests (different telegram_id)
        response = client.post(
            "/api/check",
            json={"site_url": "https://example.ru", "telegram_id": 444444444},
        )

    # Assert
    assert response.status_code == 200
