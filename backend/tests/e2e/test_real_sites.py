"""E2E tests with real HTTP requests (no mocks).

These tests make actual HTTP requests to real websites to verify
the complete SEO checker functionality end-to-end.

Run with: pytest -m e2e
Skip with: pytest -m "not e2e"

NOTE: These tests are slower and may be flaky due to network conditions.
Consider running separately from unit/integration tests.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_httpbin_basic_check(client: TestClient):
    """E2E test with httpbin.org - a simple, reliable test site.

    Note: This test makes real HTTP requests and may be slower.
    """
    response = client.post("/api/check", json={
        "site_url": "https://httpbin.org",
        "telegram_id": 999000001
    })

    assert response.status_code == 200
    data = response.json()

    # Verify complete report structure
    assert "score" in data
    assert 0 <= data["score"] <= 10

    # Should have meaningful results
    assert "problems_critical" in data
    assert "problems_important" in data
    assert "checks_ok" in data

    # Metadata should be present
    assert "metadata" in data
    assert "checked_at" in data["metadata"]
    assert data["metadata"]["checks_total"] == 6

    # All checks should have been attempted
    assert len(data["detailed_checks"]) == 6

    # Verify each check has required fields
    for check in data["detailed_checks"]:
        assert "id" in check
        assert "name" in check
        assert "status" in check
        assert check["status"] in ["ok", "partial", "problem", "error"]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_rate_limiting_real_http(client: TestClient):
    """E2E test to verify rate limiting works with real HTTP requests.

    Uses httpbin.org for actual HTTP checks.
    """
    telegram_id = 999888777

    # Make 5 requests (should all succeed)
    for i in range(5):
        response = client.post("/api/check", json={
            "site_url": "https://httpbin.org",
            "telegram_id": telegram_id
        })
        assert response.status_code == 200, f"Request {i+1}/5 should succeed"

    # 6th request should be rate limited
    response = client.post("/api/check", json={
        "site_url": "https://httpbin.org",
        "telegram_id": telegram_id
    })

    assert response.status_code == 429
    data = response.json()

    # FastAPI wraps HTTPException in 'detail'
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"]["code"] == "rate_limit_exceeded"

