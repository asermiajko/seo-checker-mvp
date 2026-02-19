"""Unit tests for headings check."""

from unittest.mock import AsyncMock

import pytest

from app.checks.base import CheckResult
from app.checks.headings import check_headings


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8")


@pytest.mark.asyncio
async def test_headings_optimal() -> None:
    """Test optimal headings structure (1 H1 + H2s)."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <body>
        <h1>Main Title</h1>
        <h2>Section 1</h2>
        <p>Content</p>
        <h2>Section 2</h2>
        <h3>Subsection</h3>
    </body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_headings("https://example.ru", mock_client)

    # Assert
    assert isinstance(result, CheckResult)
    assert result.id == "content-headings"
    assert result.name == "Headings"
    assert result.status == "ok"
    assert result.severity is None


@pytest.mark.asyncio
async def test_headings_no_h1() -> None:
    """Test no H1 (problem)."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <body>
        <h2>Section 1</h2>
        <h2>Section 2</h2>
    </body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_headings("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-headings"
    assert result.status == "problem"
    assert "H1" in result.message and "отсутствует" in result.message
    assert result.severity == "critical"


@pytest.mark.asyncio
async def test_headings_multiple_h1() -> None:
    """Test multiple H1s (partial)."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <body>
        <h1>First H1</h1>
        <h1>Second H1</h1>
        <h2>Section</h2>
    </body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_headings("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-headings"
    assert result.status == "partial"
    assert "2" in result.message or "несколько" in result.message.lower()
    assert result.severity == "important"


@pytest.mark.asyncio
async def test_headings_no_h2() -> None:
    """Test H1 but no H2 (partial)."""
    # Arrange
    mock_client = AsyncMock()
    html = """
    <html>
    <body>
        <h1>Main Title</h1>
        <p>Content without H2</p>
    </body>
    </html>
    """
    mock_client.get.return_value = MockResponse(status_code=200, text=html)

    # Act
    result = await check_headings("https://example.ru", mock_client)

    # Assert
    assert result.id == "content-headings"
    assert result.status == "partial"
    assert "H2" in result.message
    assert result.severity == "enhancement"
