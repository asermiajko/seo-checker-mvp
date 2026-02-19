"""Unit tests for robots.txt check."""

from unittest.mock import AsyncMock

import pytest

from app.checks.base import CheckResult
from app.checks.robots_txt import check_robots_txt


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text


@pytest.mark.asyncio
async def test_robots_txt_valid_with_sitemap() -> None:
    """Test valid robots.txt with User-agent and Sitemap."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = MockResponse(
        status_code=200,
        text="User-agent: *\nDisallow: /admin\nSitemap: https://example.ru/sitemap.xml",
    )

    # Act
    result = await check_robots_txt("https://example.ru", mock_client)

    # Assert
    assert isinstance(result, CheckResult)
    assert result.id == "tech-robots"
    assert result.name == "Robots.txt"
    assert result.status == "ok"
    assert "User-agent и Sitemap" in result.message
    assert result.severity is None
    assert result.category == "technical"
    mock_client.get.assert_called_once_with("https://example.ru/robots.txt", timeout=5.0)


@pytest.mark.asyncio
async def test_robots_txt_valid_without_sitemap() -> None:
    """Test valid robots.txt without Sitemap."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = MockResponse(
        status_code=200, text="User-agent: *\nDisallow: /admin"
    )

    # Act
    result = await check_robots_txt("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-robots"
    assert result.status == "partial"
    assert "отсутствует Sitemap" in result.message
    assert result.severity == "important"


@pytest.mark.asyncio
async def test_robots_txt_not_found() -> None:
    """Test robots.txt not found (404)."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = MockResponse(status_code=404, text="Not Found")

    # Act
    result = await check_robots_txt("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-robots"
    assert result.status == "problem"
    assert "не найден" in result.message
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_robots_txt_empty_file() -> None:
    """Test empty robots.txt file."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = MockResponse(status_code=200, text="")

    # Act
    result = await check_robots_txt("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-robots"
    assert result.status == "problem"
    assert "отсутствует User-agent" in result.message
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_robots_txt_timeout() -> None:
    """Test timeout during robots.txt check."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Timeout")

    # Act
    result = await check_robots_txt("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-robots"
    assert result.status == "error"
    assert "Ошибка проверки" in result.message or "Timeout" in result.message
