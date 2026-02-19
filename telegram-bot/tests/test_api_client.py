"""Unit tests for API client."""

from unittest.mock import AsyncMock, patch
import pytest
import httpx


@pytest.mark.asyncio
async def test_api_client_success():
    """Test successful API call returns report."""
    from services.api_client import APIClient

    api_client = APIClient(api_url="http://test-api.local")

    mock_response_data = {
        "score": 7.5,
        "problems_critical": 1,
        "problems_important": 1,
        "checks_ok": 5,
        "categories": [{"name": "Техническая база", "score": 4, "total": 5}],
        "top_priorities": [
            {
                "severity": "critical",
                "title": "Главная закрыта от индексации",
                "action": "Удалите noindex",
            }
        ],
        "metadata": {
            "site_url": "https://example.ru",
            "checked_at": "2026-02-19T10:00:00",
            "execution_time_sec": 25.5,
        },
    }

    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: mock_response_data
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await api_client.check_site("https://example.ru", 123456789)

    assert result["score"] == 7.5
    assert result["problems_critical"] == 1
    assert "categories" in result

    mock_client.post.assert_called_once()
    call_kwargs = mock_client.post.call_args.kwargs
    assert call_kwargs["json"]["site_url"] == "https://example.ru"
    assert call_kwargs["json"]["telegram_id"] == 123456789


@pytest.mark.asyncio
async def test_api_client_rate_limit():
    """Test API returns 429 rate limit error."""
    from services.api_client import APIClient

    api_client = APIClient(api_url="http://test-api.local")

    error_response_data = {
        "error": {
            "code": "rate_limit_exceeded",
            "message": "Вы превысили лимит проверок (5 в час). Попробуйте позже.",
            "retry_after_sec": 3600,
        }
    }

    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 429
    mock_response.json = lambda: error_response_data
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await api_client.check_site("https://example.ru", 987654321)

    assert "error" in result
    assert result["error"]["code"] == "rate_limit_exceeded"
    assert "5 в час" in result["error"]["message"]


@pytest.mark.asyncio
async def test_api_client_timeout():
    """Test API call timeout handling."""
    from services.api_client import APIClient

    api_client = APIClient(api_url="http://test-api.local", timeout=5.0)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Request timeout")

        result = await api_client.check_site("https://slow-site.ru", 111111111)

    assert "error" in result
    assert result["error"]["code"] == "timeout"
    message_lower = result["error"]["message"].lower()
    assert "врем" in message_lower or "timeout" in message_lower


@pytest.mark.asyncio
async def test_api_client_connection_error():
    """Test API call handles connection errors."""
    from services.api_client import APIClient

    api_client = APIClient(api_url="http://unreachable-api.local")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection failed")

        result = await api_client.check_site("https://example.ru", 222222222)

    assert "error" in result
    assert result["error"]["code"] == "connection_error"


@pytest.mark.asyncio
async def test_api_client_validation_error():
    """Test API returns 422 validation error."""
    from services.api_client import APIClient

    api_client = APIClient(api_url="http://test-api.local")

    error_response_data = {
        "detail": [
            {
                "loc": ["body", "site_url"],
                "msg": "invalid or missing URL scheme",
                "type": "value_error.url.scheme",
            }
        ]
    }

    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 422
    mock_response.json = lambda: error_response_data
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await api_client.check_site("invalid-url", 333333333)

    assert "error" in result
    assert result["error"]["code"] == "validation_error"
