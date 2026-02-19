# Testing Strategy

**Module**: Testing  
**Framework**: pytest, pytest-cov, pytest-asyncio  
**Last Updated**: 2026-02-18

---

## Overview

Testing follows **TDD (Test-Driven Development)**:
1. Write test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor (REFACTOR)

**Coverage Target**: 80% minimum (as per constitution)

---

## Test Pyramid

```
        ┌─────────────┐
        │  E2E Tests  │  (10%)
        │  Real sites │
        └─────────────┘
       ┌───────────────┐
       │ Integration   │  (20%)
       │ API + DB      │
       └───────────────┘
    ┌───────────────────┐
    │   Unit Tests      │  (70%)
    │   Individual      │
    │   checks, utils   │
    └───────────────────┘
```

**Rationale**: Most tests should be fast unit tests. Fewer integration and E2E tests.

---

## Test Types

### 1. Unit Tests

**Scope**: Test individual functions in isolation.

**Location**: `backend/tests/unit/`

**Examples**:
- Test each SEO check function independently
- Test report builder logic
- Test validators
- Test formatters

**Mocking**:
- Mock HTTP responses (`httpx.AsyncClient`)
- Mock database queries (`AsyncSession`)
- Mock external APIs (OpenAI, if used)

**Example**:
```python
# tests/unit/checks/test_robots_txt.py
import pytest
from app.checks.robots_txt import check_robots_txt

@pytest.mark.asyncio
async def test_robots_txt_valid(mock_http_client):
    # Arrange
    mock_http_client.get.return_value = MockResponse(
        status_code=200,
        text="User-agent: *\nSitemap: https://example.ru/sitemap.xml"
    )
    
    # Act
    result = await check_robots_txt("https://example.ru", mock_http_client)
    
    # Assert
    assert result.status == "ok"
    assert "User-agent и Sitemap" in result.message


@pytest.mark.asyncio
async def test_robots_txt_missing_sitemap(mock_http_client):
    # Arrange
    mock_http_client.get.return_value = MockResponse(
        status_code=200,
        text="User-agent: *"
    )
    
    # Act
    result = await check_robots_txt("https://example.ru", mock_http_client)
    
    # Assert
    assert result.status == "partial"
    assert "отсутствует Sitemap" in result.message
```

---

### 2. Integration Tests

**Scope**: Test multiple components together.

**Location**: `backend/tests/integration/`

**Examples**:
- Test API endpoint → checks → database
- Test bot → API → database
- Test full check flow (all 8 checks)

**Setup**:
- Use test database (SQLite or PostgreSQL)
- Real HTTP client (with mocked responses)
- Real async execution (`asyncio.gather`)

**Example**:
```python
# tests/integration/test_api_check_endpoint.py
@pytest.mark.asyncio
async def test_api_check_endpoint_success(test_client, test_db):
    # Arrange
    site_url = "https://test-good-seo.example.ru"
    
    # Act
    response = await test_client.post("/api/check", json={
        "site_url": site_url,
        "telegram_id": 123456789
    })
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= 0.0
    assert data["score"] <= 10.0
    assert "categories" in data
    assert "detailed_checks" in data
    
    # Check database
    request = test_db.query(CheckRequest).filter_by(site_url=site_url).first()
    assert request is not None
    assert request.status == "completed"
```

---

### 3. E2E Tests

**Scope**: Test entire system with real sites.

**Location**: `backend/tests/e2e/`

**Examples**:
- Test with real good SEO site (e.g., `updates.idalite.ru`)
- Test with real bad SEO site (competitor or test site)
- Test timeout scenario (very slow site)

**Caution**:
- E2E tests are slow (30-60 sec each)
- Sites may change over time
- Run less frequently (e.g., before deployment only)

**Example**:
```python
# tests/e2e/test_real_sites.py
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_good_seo_site():
    """Test with real site that has good SEO."""
    site_url = "https://updates.idalite.ru"
    
    # Call API
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json={
            "site_url": site_url,
            "telegram_id": 999999999
        }, timeout=150.0)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["score"] >= 7.0  # Expect good score
    assert data["problems_critical"] == 0


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_bad_seo_site():
    """Test with site that has SEO issues."""
    site_url = "https://bad-seo-test.example.ru"
    
    # Call API
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json={
            "site_url": site_url,
            "telegram_id": 999999999
        }, timeout=150.0)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["score"] < 5.0  # Expect low score
    assert data["problems_critical"] > 0
```

---

## TDD Workflow

### Example: Implementing `check_robots_txt`

#### Step 1: Write Test (RED)

```python
# tests/unit/checks/test_robots_txt.py
@pytest.mark.asyncio
async def test_robots_txt_valid(mock_http_client):
    mock_http_client.get.return_value = MockResponse(
        status_code=200,
        text="User-agent: *\nSitemap: https://example.ru/sitemap.xml"
    )
    
    result = await check_robots_txt("https://example.ru", mock_http_client)
    
    assert result.status == "ok"
```

**Run test**:
```bash
pytest tests/unit/checks/test_robots_txt.py
```

**Result**: ❌ FAIL (function doesn't exist yet)

---

#### Step 2: Write Minimal Code (GREEN)

```python
# app/checks/robots_txt.py
async def check_robots_txt(site_url: str, client):
    response = await client.get(f"{site_url}/robots.txt")
    
    if response.status_code == 200:
        content = response.text.lower()
        if "user-agent:" in content and "sitemap:" in content:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="ok",
                message="✅ Файл найден, содержит User-agent и Sitemap"
            )
    
    return CheckResult(
        id="tech-robots",
        name="Robots.txt",
        status="problem",
        message="❌ Файл robots.txt не найден",
        severity="critical"
    )
```

**Run test**:
```bash
pytest tests/unit/checks/test_robots_txt.py
```

**Result**: ✅ PASS

---

#### Step 3: Add More Tests

```python
@pytest.mark.asyncio
async def test_robots_txt_missing_sitemap(mock_http_client):
    mock_http_client.get.return_value = MockResponse(
        status_code=200,
        text="User-agent: *"
    )
    
    result = await check_robots_txt("https://example.ru", mock_http_client)
    
    assert result.status == "partial"


@pytest.mark.asyncio
async def test_robots_txt_not_found(mock_http_client):
    mock_http_client.get.return_value = MockResponse(status_code=404)
    
    result = await check_robots_txt("https://example.ru", mock_http_client)
    
    assert result.status == "problem"
    assert result.severity == "critical"
```

---

#### Step 4: Refactor

- Add error handling
- Add timeout
- Extract constants
- Add docstring

```python
async def check_robots_txt(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """
    Check robots.txt presence and content.
    
    Args:
        site_url: Site URL (e.g., "https://example.ru")
        client: Async HTTP client
        
    Returns:
        CheckResult with status: ok, partial, problem, or error
    """
    url = f"{site_url}/robots.txt"
    
    try:
        response = await client.get(url, timeout=5.0)
        
        if response.status_code != 200:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="problem",
                message="❌ Файл robots.txt не найден",
                severity="critical"
            )
        
        content = response.text.lower()
        has_user_agent = "user-agent:" in content
        has_sitemap = "sitemap:" in content
        
        if has_user_agent and has_sitemap:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="ok",
                message="✅ Файл найден, содержит User-agent и Sitemap"
            )
        elif has_user_agent:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="partial",
                message="⚠️ Файл найден, но отсутствует Sitemap",
                severity="important"
            )
        else:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="problem",
                message="❌ Файл найден, но отсутствует User-agent",
                severity="critical"
            )
    
    except httpx.TimeoutException:
        return CheckResult(
            id="tech-robots",
            name="Robots.txt",
            status="error",
            message="⚠️ Timeout при проверке robots.txt"
        )
    except Exception as e:
        return CheckResult(
            id="tech-robots",
            name="Robots.txt",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}"
        )
```

---

## Test Fixtures

### Shared Fixtures

```python
# conftest.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine

@pytest.fixture
async def test_client():
    """FastAPI test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_db():
    """Test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for unit tests."""
    return MagicMock(spec=httpx.AsyncClient)
```

---

## Test Data

### Mock HTML Files

```
tests/fixtures/
├── html/
│   ├── good_seo.html       # All checks pass
│   ├── bad_seo.html        # All checks fail
│   ├── partial_seo.html    # Mixed results
│   ├── noindex.html        # Has noindex meta tag
│   └── no_title.html       # Missing title
├── xml/
│   ├── valid_sitemap.xml
│   ├── empty_sitemap.xml
│   └── invalid_sitemap.xml
└── txt/
    ├── valid_robots.txt
    ├── no_sitemap_robots.txt
    └── empty_robots.txt
```

See [test-data.md](./test-data.md) for content examples.

---

## Running Tests

### All Tests

```bash
pytest
```

### Specific Module

```bash
pytest tests/unit/checks/
```

### With Coverage

```bash
pytest --cov=app --cov-report=html
```

### E2E Only

```bash
pytest -m e2e
```

### Skip E2E

```bash
pytest -m "not e2e"
```

---

## Coverage Requirements

**Minimum**: 80% (as per constitution)

**Check Coverage**:
```bash
pytest --cov=app --cov-report=term-missing
```

**Exclude from Coverage**:
- `__init__.py`
- Test files
- Migration scripts

---

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Check coverage
        run: |
          coverage report --fail-under=80
```

---

## Next Steps

1. Review this strategy
2. Create test fixtures (see [test-data.md](./test-data.md))
3. Start implementing checks with TDD
4. Aim for 80%+ coverage

---

**Related Documents**:
- [Test Data](./test-data.md)
- [MVP Checks](../checks/mvp-checks.md)
- [API Contracts](../api/contracts.md)
