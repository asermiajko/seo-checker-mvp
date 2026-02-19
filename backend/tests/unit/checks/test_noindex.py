"""Unit tests for noindex check."""

from unittest.mock import AsyncMock

import pytest

from app.checks.base import CheckResult
from app.checks.noindex import check_noindex


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, text: str = "", headers: dict = None) -> None:
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8")
        self.headers = headers or {}


@pytest.mark.asyncio
async def test_noindex_not_found() -> None:
    """Test no noindex (good case)."""
    # Arrange
    mock_client = AsyncMock()
    html_without_noindex = """
    <html>
    <head>
        <title>Example</title>
    </head>
    <body>Content</body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html_without_noindex)

    # Act
    result = await check_noindex("https://example.ru", mock_client)

    # Assert
    assert isinstance(result, CheckResult)
    assert result.id == "tech-noindex"
    assert result.status == "ok"
    assert "не найден" in result.message or "отсутствует" in result.message
    assert result.severity is None


@pytest.mark.asyncio
async def test_noindex_meta_tag_found() -> None:
    """Test noindex in meta tag (bad case)."""
    # Arrange
    mock_client = AsyncMock()
    html_with_noindex = """
    <html>
    <head>
        <meta name="robots" content="noindex, nofollow">
        <title>Example</title>
    </head>
    <body>Content</body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html_with_noindex)

    # Act
    result = await check_noindex("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-noindex"
    assert result.status == "problem"
    assert "noindex" in result.message.lower()
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_noindex_http_header() -> None:
    """Test noindex in X-Robots-Tag header."""
    # Arrange
    mock_client = AsyncMock()
    headers = {"X-Robots-Tag": "noindex"}
    mock_client.get.return_value = MockResponse(
        status_code=200, text="<html><body>Content</body></html>", headers=headers
    )

    # Act
    result = await check_noindex("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-noindex"
    assert result.status == "problem"
    assert "noindex" in result.message.lower()
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_noindex_page_unreachable() -> None:
    """Test page unreachable."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = MockResponse(status_code=404)

    # Act
    result = await check_noindex("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-noindex"
    assert result.status == "error"
