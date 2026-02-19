"""Unit tests for sitemap.xml check."""

from unittest.mock import AsyncMock

import pytest

from app.checks.base import CheckResult
from app.checks.sitemap_xml import check_sitemap_xml


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, content: bytes = b"") -> None:
        self.status_code = status_code
        self.content = content


@pytest.mark.asyncio
async def test_sitemap_xml_valid_with_urls() -> None:
    """Test valid sitemap with URLs."""
    # Arrange
    mock_client = AsyncMock()
    sitemap_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.ru/</loc>
    <lastmod>2024-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.ru/about</loc>
  </url>
</urlset>"""
    mock_client.get.return_value = MockResponse(status_code=200, content=sitemap_xml)

    # Act
    result = await check_sitemap_xml("https://example.ru", mock_client)

    # Assert
    assert isinstance(result, CheckResult)
    assert result.id == "tech-sitemap"
    assert result.name == "Sitemap.xml"
    assert result.status == "ok"
    assert "содержит" in result.message and "URL" in result.message
    assert result.severity is None
    mock_client.get.assert_called_once_with("https://example.ru/sitemap.xml", timeout=10.0)


@pytest.mark.asyncio
async def test_sitemap_xml_sitemap_index() -> None:
    """Test sitemap index (multiple sitemaps)."""
    # Arrange
    mock_client = AsyncMock()
    sitemap_index = b"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.ru/sitemap-posts.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.ru/sitemap-pages.xml</loc>
  </sitemap>
</sitemapindex>"""
    mock_client.get.return_value = MockResponse(status_code=200, content=sitemap_index)

    # Act
    result = await check_sitemap_xml("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-sitemap"
    assert result.status == "partial"
    assert "sitemap index" in result.message.lower()
    assert result.severity == "enhancement"


@pytest.mark.asyncio
async def test_sitemap_xml_not_found() -> None:
    """Test sitemap.xml not found (404)."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.get.return_value = MockResponse(status_code=404)

    # Act
    result = await check_sitemap_xml("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-sitemap"
    assert result.status == "problem"
    assert "не найден" in result.message
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_sitemap_xml_invalid_xml() -> None:
    """Test invalid XML in sitemap."""
    # Arrange
    mock_client = AsyncMock()
    invalid_xml = b"This is not XML at all!"
    mock_client.get.return_value = MockResponse(status_code=200, content=invalid_xml)

    # Act
    result = await check_sitemap_xml("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-sitemap"
    assert result.status == "problem"
    assert "невалидный XML" in result.message or "XML" in result.message
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_sitemap_xml_empty() -> None:
    """Test empty sitemap (no URLs)."""
    # Arrange
    mock_client = AsyncMock()
    empty_sitemap = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
    mock_client.get.return_value = MockResponse(status_code=200, content=empty_sitemap)

    # Act
    result = await check_sitemap_xml("https://example.ru", mock_client)

    # Assert
    assert result.id == "tech-sitemap"
    assert result.status == "problem"
    assert "не содержит URL" in result.message
    assert result.severity == "important"
