"""Unit tests for analytics check."""

from unittest.mock import AsyncMock

import pytest

from app.checks.analytics import check_analytics
from app.checks.base import CheckResult


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text


@pytest.mark.asyncio
async def test_analytics_yandex_metrika() -> None:
    """Test Yandex.Metrika found."""
    # Arrange
    mock_client = AsyncMock()
    html_with_metrika = """
    <html>
    <head>
        <script src="https://mc.yandex.ru/metrika/tag.js"></script>
    </head>
    <body>Content</body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html_with_metrika)

    # Act
    result = await check_analytics("https://example.ru", mock_client)

    # Assert
    assert isinstance(result, CheckResult)
    assert result.id == "tech-analytics"
    assert result.status == "ok"
    assert "Yandex.Metrika" in result.message or "Метрика" in result.message
    assert result.severity is None


@pytest.mark.asyncio
async def test_analytics_google_analytics() -> None:
    """Test Google Analytics found."""
    # Arrange
    mock_client = AsyncMock()
    html_with_ga = """
    <html>
    <head>
        <script async src="https://www.googletagmanager.com/gtag/js"></script>
    </head>
    <body>Content</body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html_with_ga)

    # Act
    result = await check_analytics("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-analytics"
    assert result.status == "ok"
    assert "Google" in result.message


@pytest.mark.asyncio
async def test_analytics_both_found() -> None:
    """Test both Yandex and Google found."""
    # Arrange
    mock_client = AsyncMock()
    html_with_both = """
    <html>
    <head>
        <script src="https://mc.yandex.ru/metrika/tag.js"></script>
        <script src="https://www.googletagmanager.com/gtag/js"></script>
    </head>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html_with_both)

    # Act
    result = await check_analytics("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-analytics"
    assert result.status == "ok"
    assert "Yandex.Metrika" in result.message or "Google" in result.message


@pytest.mark.asyncio
async def test_analytics_none_found() -> None:
    """Test no analytics counters found."""
    # Arrange
    mock_client = AsyncMock()
    html_without_analytics = "<html><body>No analytics here</body></html>"
    mock_client.get.return_value = MockResponse(status_code=200, text=html_without_analytics)

    # Act
    result = await check_analytics("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-analytics"
    assert result.status == "problem"
    assert "не найдены" in result.message or "не установлены" in result.message
    assert result.severity == "important"
