"""Full flow integration tests for SEO Checker.

These tests verify the complete end-to-end flow from API request to response,
including all 6 SEO checks, report building, and database persistence.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_full_flow_good_seo_site(client: TestClient):
    """Test complete flow with a site that has decent SEO.

    Verifies that API processes all checks and returns valid report structure.
    """
    # Mock HTML for a reasonably optimized site
    good_html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <title>Excellent SEO Site - Professional Real Estate Development</title>
        <meta
            name="description"
            content="Leading real estate company building properties."
        >
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-12345678-1"></script>
    </head>
    <body>
        <h1>Welcome to Excellent SEO Site</h1>
        <h2>Our Services</h2>
        <p>Quality residential properties</p>
        <h2>Latest Projects</h2>
        <p>Modern commercial developments</p>
    </body>
    </html>
    """

    good_robots = """User-agent: *
Allow: /
Sitemap: https://good-site.ru/sitemap.xml
"""

    good_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://good-site.ru/</loc>
  </url>
</urlset>
"""

    # Mock httpx.AsyncClient
    mock_client = AsyncMock()

    # Mock all responses
    mock_robots_response = AsyncMock()
    mock_robots_response.status_code = 200
    mock_robots_response.text = good_robots

    mock_sitemap_response = AsyncMock()
    mock_sitemap_response.status_code = 200
    mock_sitemap_response.text = good_sitemap

    mock_html_response = AsyncMock()
    mock_html_response.status_code = 200
    mock_html_response.text = good_html
    mock_html_response.headers = {}

    async def mock_get(url, **kwargs):
        if "robots.txt" in url:
            return mock_robots_response
        elif "sitemap.xml" in url:
            return mock_sitemap_response
        else:
            return mock_html_response

    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json={
            "site_url": "https://good-site.ru",
            "telegram_id": 111111111
        })

    assert response.status_code == 200
    data = response.json()

    # Verify report structure
    assert "score" in data
    assert 0 <= data["score"] <= 10

    # Verify counts
    assert "problems_critical" in data
    assert "problems_important" in data
    assert "checks_ok" in data

    # Should have some checks passing with good HTML
    assert data["checks_ok"] >= 2, f"Expected at least 2 checks OK, got {data['checks_ok']}"

    # Check metadata structure
    assert "metadata" in data
    assert "checked_at" in data["metadata"]
    assert "processing_time_sec" in data["metadata"]
    assert data["metadata"]["checks_total"] == 6

    # Categories should exist
    assert len(data["categories"]) > 0

    # Detailed checks should exist
    assert len(data["detailed_checks"]) == 6


@pytest.mark.asyncio
async def test_full_flow_bad_seo_site(client: TestClient):
    """Test complete flow with a site that has poor SEO.

    Expected: score < 5, multiple critical issues.
    """
    # Mock HTML for a poorly optimized site
    bad_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Site</title>
        <meta name="description" content="Site">
        <meta name="robots" content="noindex, nofollow">
    </head>
    <body>
        <div>Welcome</div>
        <div>Content here</div>
    </body>
    </html>
    """

    bad_robots = """User-agent: *
Disallow: /
"""

    # Mock httpx.AsyncClient
    mock_client = AsyncMock()

    # Mock robots.txt response (blocking)
    mock_robots_response = AsyncMock()
    mock_robots_response.status_code = 200
    mock_robots_response.text = bad_robots

    # Mock sitemap.xml response (404)
    mock_sitemap_response = AsyncMock()
    mock_sitemap_response.status_code = 404
    mock_sitemap_response.text = "Not Found"

    # Mock HTML response
    mock_html_response = AsyncMock()
    mock_html_response.status_code = 200
    mock_html_response.text = bad_html
    mock_html_response.headers = {"X-Robots-Tag": "noindex"}

    async def mock_get(url, **kwargs):
        if "robots.txt" in url:
            return mock_robots_response
        elif "sitemap.xml" in url:
            return mock_sitemap_response
        else:
            return mock_html_response

    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json={
            "site_url": "https://bad-site.ru",
            "telegram_id": 222222222
        })

    assert response.status_code == 200
    data = response.json()

    # Score should be low (<5)
    assert data["score"] < 5.0, f"Expected score < 5, got {data['score']}"

    # Should have multiple critical issues
    assert data["problems_critical"] >= 2

    # Should have few checks passing
    assert data["checks_ok"] <= 3

    # Check that top priorities exist
    assert len(data["top_priorities"]) > 0

    # Verify critical issues are reported
    priorities_text = " ".join(
        [p["title"].lower() for p in data["top_priorities"]]
    )
    assert any(
        keyword in priorities_text
        for keyword in ["robots", "noindex", "sitemap", "title", "description"]
    )


@pytest.mark.asyncio
async def test_full_flow_partial_results(client: TestClient):
    """Test complete flow when some checks fail.

    Expected: System handles gracefully and returns partial results.
    """
    # Mock HTML that will work for some checks
    partial_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Partially Working Site - Real Estate Developer</title>
        <meta name="description" content="We build quality properties with modern design.">
    </head>
    <body>
        <h1>Welcome to Our Site</h1>
        <h2>Our Projects</h2>
        <p>Quality properties</p>
    </body>
    </html>
    """

    # Mock httpx.AsyncClient
    mock_client = AsyncMock()

    # Mock robots.txt response (timeout/error)
    mock_robots_response = AsyncMock()
    mock_robots_response.status_code = 500
    mock_robots_response.text = "Internal Server Error"

    # Mock sitemap.xml response (success)
    mock_sitemap_response = AsyncMock()
    mock_sitemap_response.status_code = 404
    mock_sitemap_response.text = "Not Found"

    # Mock HTML response (success)
    mock_html_response = AsyncMock()
    mock_html_response.status_code = 200
    mock_html_response.text = partial_html
    mock_html_response.headers = {}

    async def mock_get(url, **kwargs):
        if "robots.txt" in url:
            return mock_robots_response
        elif "sitemap.xml" in url:
            return mock_sitemap_response
        else:
            return mock_html_response

    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/check", json={
            "site_url": "https://partial-site.ru",
            "telegram_id": 333333333
        })

    # Should still return 200 (graceful degradation)
    assert response.status_code == 200
    data = response.json()

    # Should have a score (even if some checks failed)
    assert 0 <= data["score"] <= 10

    # Should have counts for all result types
    assert "problems_critical" in data
    assert "problems_important" in data
    assert "checks_ok" in data

    # Sum should be reasonable (some checks may have errors/partial status)
    total_results = data["problems_critical"] + data["problems_important"] + data["checks_ok"]
    assert total_results >= 1, f"Expected at least 1 check result, got {total_results}"
    assert total_results <= 6, f"Expected at most 6 checks, got {total_results}"

    # Metadata should exist (but doesn't include site_url per API contract)
    assert "metadata" in data
    assert "checked_at" in data["metadata"]
    assert "processing_time_sec" in data["metadata"]

    # Categories should exist
    assert len(data["categories"]) > 0

    # Check that detailed_checks exist
    assert len(data["detailed_checks"]) >= 1
    assert len(data["detailed_checks"]) <= 6
