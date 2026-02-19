"""Integration tests for error handling."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_error_handling_does_not_crash_api(client: TestClient) -> None:
    """Test that API handles errors gracefully."""
    request_data = {"site_url": "https://example.ru", "telegram_id": 555555555}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=AsyncMock(status_code=500, text="Error"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "metadata" in data


@pytest.mark.asyncio
async def test_error_handling_invalid_html(client: TestClient) -> None:
    """Test handling of malformed HTML."""
    request_data = {"site_url": "https://broken.ru", "telegram_id": 666666666}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        return_value=AsyncMock(status_code=200, text="Not HTML <><>")
    )
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["checks_total"] == 6


@pytest.mark.asyncio
async def test_error_handling_database_persistence(client: TestClient) -> None:
    """Test that database saves data even with errors."""
    request_data = {"site_url": "https://test.ru", "telegram_id": 777777777}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        return_value=AsyncMock(status_code=200, text="User-agent: *\nSitemap: /s.xml")
    )
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "checked_at" in data["metadata"]

