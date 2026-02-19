"""Unit tests for meta tags check."""

from unittest.mock import AsyncMock

import pytest

from app.checks.base import CheckResult
from app.checks.meta_tags import check_meta_tags


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8")


@pytest.mark.asyncio
async def test_meta_tags_optimal() -> None:
    """Test optimal meta tags (title 30-65, description 120-160)."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <head>
        <title>This is a good title between 30 and 65 characters</title>
        <meta
            name="description"
            content="Excellent comprehensive description providing detailed information about page content, optimized for search engines with proper length requirements."
        >
    </head>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_meta_tags("https://example.ru", mock_client)

    # Assert
    assert isinstance(result, CheckResult)
    assert result.id == "content-meta"
    assert result.status == "ok"
    assert result.severity is None


@pytest.mark.asyncio
async def test_meta_tags_missing_title() -> None:
    """Test missing title."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <head>
        <meta name="description" content="Description is here">
    </head>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_meta_tags("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-meta"
    assert result.status == "problem"
    assert "title" in result.message.lower() or "заголовок" in result.message.lower()
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_meta_tags_short_title() -> None:
    """Test title too short (< 30 chars)."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <head>
        <title>Short</title>
        <meta
            name="description"
            content="This is a good description that is between 120 and 160 characters long."
        >
    </head>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_meta_tags("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-meta"
    assert result.status == "partial"
    assert result.severity == "important"


@pytest.mark.asyncio
async def test_meta_tags_long_description() -> None:
    """Test description too long (> 160 chars)."""
    # Arrange
    mock_client = AsyncMock()
    html = f"""
    <html>
    <head>
        <title>This is a good title between 30 and 65 characters</title>
        <meta name="description" content="{'x' * 200}">
    </head>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_meta_tags("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-meta"
    assert result.status == "partial"
    assert result.severity == "important"


@pytest.mark.asyncio
async def test_meta_tags_both_missing() -> None:
    """Test both title and description missing."""
    # Arrange
    mock_client = AsyncMock()
    html = "<html><head></head><body>Content</body></html>"
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_meta_tags("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-meta"
    assert result.status == "problem"
    assert result.severity == "critical"
