# Task Breakdown: SEO Checker MVP

**Spec ID**: 001-seo-checker  
**Phase**: Tasks  
**Created**: 2026-02-18  
**Status**: Ready for Implementation

> **Navigation**: See [PLAN.md](./PLAN.md) for module details and [README.md](./README.md) for full documentation.

---

## Overview

This document breaks down the implementation plan into **42 concrete tasks** following TDD methodology.

**Total Estimated Time**: 25-32 hours

**Task Types**:
- `[CONFIG]` — Configuration, setup, infrastructure
- `[TEST]` — Write tests (RED phase)
- `[IMPL]` — Implementation (GREEN phase)
- `[REFACTOR]` — Code improvement, optimization

**Status Legend**:
- ⏳ Not Started
- 🔄 In Progress
- ✅ Completed
- ⏭️ Blocked (waiting for dependencies)

---

## Module 1: Project Setup (2-3 hours)

### TASK-001: Initialize Project Structure
**Type**: `[CONFIG]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Create directory structure and base files.

**Files to Create**:
```
seo-checker-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── routes/
│   │   │   └── __init__.py
│   │   ├── checks/
│   │   │   └── __init__.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   └── __init__.py
│   │   ├── integration/
│   │   │   └── __init__.py
│   │   └── e2e/
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── telegram-bot/
    ├── bot.py
    ├── handlers/
    │   └── __init__.py
    ├── services/
    │   └── __init__.py
    ├── tests/
    │   └── __init__.py
    ├── requirements.txt
    ├── .env.example
    └── README.md
```

**Commands**:
```bash
cd /Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool
mkdir -p backend/app/{routes,checks,utils}
mkdir -p backend/tests/{unit/checks,integration,e2e}
mkdir -p telegram-bot/{handlers,services,tests}
touch backend/app/__init__.py backend/app/main.py
# ... create all files
```

**Acceptance Criteria**:
- ✅ All directories created
- ✅ All `__init__.py` files present
- ✅ Base `main.py` with "Hello World" FastAPI app
- ✅ Can import modules without errors

**Dependencies**: None

---

### TASK-002: Setup Dependencies
**Type**: `[CONFIG]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Create requirements.txt and install dependencies.

**Files to Create/Modify**:
- `backend/requirements.txt`
- `telegram-bot/requirements.txt`

**Backend Dependencies**:
```txt
# backend/requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
beautifulsoup4==4.12.3
lxml==5.1.0

# Development
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
ruff==0.1.14
mypy==1.8.0
```

**Bot Dependencies**:
```txt
# telegram-bot/requirements.txt
python-telegram-bot==20.7
httpx==0.26.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Development
pytest==7.4.4
pytest-asyncio==0.23.3
```

**Commands**:
```bash
cd backend/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd ../telegram-bot/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Acceptance Criteria**:
- ✅ Both virtual environments created
- ✅ All dependencies installed
- ✅ `pip list` shows correct versions
- ✅ No import errors

**Dependencies**: TASK-001

---

### TASK-003: Configure Linters
**Type**: `[CONFIG]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Setup ruff and mypy for code quality.

**Files to Create**:
- `backend/pyproject.toml`
- `backend/.ruff.toml`
- `backend/mypy.ini`

**backend/pyproject.toml**:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"
```

**backend/mypy.ini**:
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

**Commands**:
```bash
cd backend/
ruff check app/
mypy app/
```

**Acceptance Criteria**:
- ✅ Ruff configured and runs without errors
- ✅ Mypy configured
- ✅ Can run linters on codebase
- ✅ Pre-commit hook optional (can add later)

**Dependencies**: TASK-002

---

### TASK-004: Setup Database Schema
**Type**: `[CONFIG]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Create database models and initial migration.

**Files to Create**:
- `backend/app/database.py` — DB connection
- `backend/app/models.py` — SQLAlchemy models
- `backend/migrations/001_initial_schema.sql` — SQL migration

**Reference**: [database/schema.md](./database/schema.md)

**backend/app/database.py**:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/seo_checker"
    
    class Config:
        env_file = ".env"

settings = Settings()
engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

**backend/app/models.py**:
```python
from sqlalchemy import Column, Integer, String, BigInteger, DECIMAL, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .database import Base

class CheckRequest(Base):
    __tablename__ = "check_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    site_url = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    result = relationship("CheckResult", back_populates="request", uselist=False)

class CheckResult(Base):
    __tablename__ = "check_results"
    
    id = Column(Integer, primary_key=True, index=True)
    check_request_id = Column(Integer, ForeignKey("check_requests.id", ondelete="CASCADE"))
    score = Column(DECIMAL(3, 1), nullable=False)
    problems_critical = Column(Integer, default=0)
    problems_important = Column(Integer, default=0)
    checks_ok = Column(Integer, default=0)
    report_data = Column(JSONB, nullable=False)
    detailed_checks = Column(JSONB, nullable=False)
    processing_time_sec = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    
    request = relationship("CheckRequest", back_populates="result")
```

**Commands**:
```bash
# Local PostgreSQL (Docker)
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=seo_checker \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=seo_checker \
  postgres:14

# Run migration
psql postgresql://seo_checker:dev@localhost/seo_checker \
  -f backend/migrations/001_initial_schema.sql
```

**Acceptance Criteria**:
- ✅ Database connection works
- ✅ Models defined (CheckRequest, CheckResult)
- ✅ Migration creates tables
- ✅ Can query database with SQLAlchemy

**Dependencies**: TASK-002

---

## Module 2: Core Checks (8-10 hours)

### TASK-005: [TEST] Robots.txt Check
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write unit tests for robots.txt check.

**Files to Create**:
- `backend/tests/unit/checks/test_robots_txt.py`
- `backend/tests/conftest.py` — Shared fixtures

**Test Cases**:
1. Valid robots.txt with User-agent and Sitemap → `status="ok"`
2. Valid robots.txt without Sitemap → `status="partial"`
3. 404 Not Found → `status="problem"`
4. Empty file → `status="problem"`
5. Timeout → `status="error"`

**Example Test**:
```python
import pytest
from app.checks.robots_txt import check_robots_txt
from app.checks.base import CheckResult

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
    assert result.severity is None
```

**Reference**: [checks/mvp-checks.md#check-1-robotstxt](./checks/mvp-checks.md#check-1-robotstxt)

**Acceptance Criteria**:
- ✅ 5 test cases written
- ✅ Tests fail (RED) because implementation doesn't exist yet
- ✅ Tests use mocked HTTP client
- ✅ Clear, descriptive test names

**Dependencies**: TASK-004

---

### TASK-006: [IMPL] Robots.txt Check
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement robots.txt check to pass tests.

**Files to Create**:
- `backend/app/checks/base.py` — CheckResult dataclass
- `backend/app/checks/robots_txt.py` — Implementation

**backend/app/checks/base.py**:
```python
from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class CheckResult:
    id: str
    name: str
    status: Literal["ok", "partial", "problem", "error"]
    message: str
    severity: Optional[Literal["critical", "important", "enhancement"]] = None
    category: str = "technical"
```

**backend/app/checks/robots_txt.py**:
```python
import httpx
from .base import CheckResult

async def check_robots_txt(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check robots.txt presence and content."""
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

**Commands**:
```bash
cd backend/
pytest tests/unit/checks/test_robots_txt.py -v
```

**Acceptance Criteria**:
- ✅ All 5 tests pass (GREEN)
- ✅ Type hints on all functions
- ✅ Docstring present
- ✅ Handles all edge cases

**Dependencies**: TASK-005

---

### TASK-007: [TEST] Sitemap.xml Check
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write unit tests for sitemap.xml check.

**Files to Create**:
- `backend/tests/unit/checks/test_sitemap_xml.py`

**Test Cases**:
1. Valid sitemap with URLs → `status="ok"`
2. Sitemap index → `status="partial"`
3. 404 Not Found → `status="problem"`
4. Invalid XML → `status="problem"`
5. Empty sitemap → `status="problem"`

**Reference**: [checks/mvp-checks.md#check-2-sitemapxml](./checks/mvp-checks.md#check-2-sitemapxml)

**Acceptance Criteria**:
- ✅ 5 test cases written
- ✅ Tests fail (RED)
- ✅ Mocked XML responses

**Dependencies**: TASK-006

---

### TASK-008: [IMPL] Sitemap.xml Check
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement sitemap.xml check.

**Files to Create**:
- `backend/app/checks/sitemap_xml.py`

**Implementation**: XML parsing with `xml.etree.ElementTree`

**Acceptance Criteria**:
- ✅ All tests pass (GREEN)
- ✅ Handles namespaces correctly
- ✅ Distinguishes between sitemap and sitemap index

**Dependencies**: TASK-007

---

### TASK-009: [TEST] Analytics Check
**Type**: `[TEST]`  
**Time**: 20 min  
**Status**: ⏳

**Description**: Write unit tests for analytics counters check.

**Files to Create**:
- `backend/tests/unit/checks/test_analytics.py`

**Test Cases**:
1. Yandex.Metrika found → `status="ok"`
2. Google Analytics found → `status="ok"`
3. Both found → `status="ok"`
4. None found → `status="problem"`

**Reference**: [checks/mvp-checks.md#check-6-analytics-counters](./checks/mvp-checks.md#check-6-analytics-counters)

**Acceptance Criteria**:
- ✅ 4 test cases written
- ✅ Tests fail (RED)

**Dependencies**: TASK-008

---

### TASK-010: [IMPL] Analytics Check
**Type**: `[IMPL]`  
**Time**: 45 min  
**Status**: ⏳

**Description**: Implement analytics check.

**Files to Create**:
- `backend/app/checks/analytics.py`

**Implementation**: Search HTML for:
- `mc.yandex.ru/metrika`
- `googletagmanager.com/gtag`
- `google-analytics.com/analytics.js`

**Acceptance Criteria**:
- ✅ All tests pass (GREEN)
- ✅ Detects both Yandex and Google

**Dependencies**: TASK-009

---

### TASK-011: [TEST] Noindex Check
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write unit tests for noindex check.

**Files to Create**:
- `backend/tests/unit/checks/test_noindex.py`

**Test Cases**:
1. No noindex meta tag → `status="ok"`
2. Noindex found → `status="problem"` (critical)
3. X-Robots-Tag header with noindex → `status="problem"`
4. Page unreachable → `status="error"`

**Reference**: [checks/mvp-checks.md#check-3-noindex-on-main-page](./checks/mvp-checks.md#check-3-noindex-on-main-page)

**Acceptance Criteria**:
- ✅ 4 test cases written
- ✅ Tests fail (RED)

**Dependencies**: TASK-010

---

### TASK-012: [IMPL] Noindex Check
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement noindex check.

**Files to Create**:
- `backend/app/checks/noindex.py`

**Implementation**:
- Parse HTML with BeautifulSoup
- Check `<meta name="robots" content="noindex">`
- Check HTTP headers `X-Robots-Tag`

**Acceptance Criteria**:
- ✅ All tests pass (GREEN)
- ✅ Checks both meta tag and HTTP header

**Dependencies**: TASK-011

---

### TASK-013: [TEST] Meta Tags Check
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write unit tests for meta tags check.

**Files to Create**:
- `backend/tests/unit/checks/test_meta_tags.py`

**Test Cases**:
1. Optimal title & description → `status="ok"`
2. Missing title → `status="problem"`
3. Short title (< 30 chars) → `status="partial"`
4. Long description (> 160 chars) → `status="partial"`
5. Both missing → `status="problem"`

**Reference**: [checks/mvp-checks.md#check-4-meta-tags](./checks/mvp-checks.md#check-4-meta-tags)

**Acceptance Criteria**:
- ✅ 5 test cases written
- ✅ Tests fail (RED)

**Dependencies**: TASK-012

---

### TASK-014: [IMPL] Meta Tags Check
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement meta tags check.

**Files to Create**:
- `backend/app/checks/meta_tags.py`

**Implementation**:
- Extract `<title>` and `<meta name="description">`
- Check lengths (title: 30-65, description: 120-160)
- Return appropriate status

**Acceptance Criteria**:
- ✅ All tests pass (GREEN)
- ✅ Correct length validation

**Dependencies**: TASK-013

---

### TASK-015: [TEST] Headings Check
**Type**: `[TEST]`  
**Time**: 20 min  
**Status**: ⏳

**Description**: Write unit tests for headings check.

**Files to Create**:
- `backend/tests/unit/checks/test_headings.py`

**Test Cases**:
1. 1 H1 + H2s → `status="ok"`
2. No H1 → `status="problem"`
3. Multiple H1s → `status="partial"`
4. H1 but no H2 → `status="partial"`

**Reference**: [checks/mvp-checks.md#check-5-h1h2-structure](./checks/mvp-checks.md#check-5-h1h2-structure)

**Acceptance Criteria**:
- ✅ 4 test cases written
- ✅ Tests fail (RED)

**Dependencies**: TASK-014

---

### TASK-016: [IMPL] Headings Check
**Type**: `[IMPL]`  
**Time**: 45 min  
**Status**: ⏳

**Description**: Implement headings check.

**Files to Create**:
- `backend/app/checks/headings.py`

**Implementation**:
- Find all `<h1>` and `<h2>` tags
- Count them
- Return status based on counts

**Acceptance Criteria**:
- ✅ All tests pass (GREEN)
- ✅ Correct H1/H2 validation

**Dependencies**: TASK-015

---

## Module 3: Report Builder (2 hours)

### TASK-017: [TEST] Score Calculator
**Type**: `[TEST]`  
**Time**: 20 min  
**Status**: ⏳

**Description**: Write tests for score calculation.

**Files to Create**:
- `backend/tests/unit/test_report_builder.py`

**Test Cases**:
1. All checks ok (6/6) → score = 10.0
2. 5 ok + 1 partial → score = 9.2
3. 4 ok + 2 problem → score = 6.7
4. All problem → score = 0.0

**Formula**: `(ok * 1.0 + partial * 0.5) / total * 10`

**Acceptance Criteria**:
- ✅ 4 test cases written
- ✅ Tests fail (RED)

**Dependencies**: TASK-016

---

### TASK-018: [IMPL] Report Builder
**Type**: `[IMPL]`  
**Time**: 1.5 hours  
**Status**: ⏳

**Description**: Implement report builder logic.

**Files to Create**:
- `backend/app/report_builder.py`

**Functions**:
1. `calculate_score(checks: list[CheckResult]) -> float`
2. `group_by_category(checks: list[CheckResult]) -> list[dict]`
3. `extract_top_priorities(checks: list[CheckResult]) -> list[dict]`
4. `build_report(checks: list[CheckResult]) -> dict`

**Reference**: [api/contracts.md](./api/contracts.md)

**Acceptance Criteria**:
- ✅ All tests pass (GREEN)
- ✅ Correct score calculation
- ✅ Categories grouped
- ✅ Top 3 priorities extracted

**Dependencies**: TASK-017

---

## Module 4: Backend API (4-5 hours)

### TASK-019: [TEST] API Endpoint - Happy Path
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write integration test for successful check.

**Files to Create**:
- `backend/tests/integration/test_api_check_endpoint.py`

**Test Case**: POST /api/check with valid URL → 200 OK + full report

**Acceptance Criteria**:
- ✅ Test written
- ✅ Test fails (RED)
- ✅ Uses test database

**Dependencies**: TASK-018

---

### TASK-020: [IMPL] API Endpoint
**Type**: `[IMPL]`  
**Time**: 2 hours  
**Status**: ⏳

**Description**: Implement POST /api/check endpoint.

**Files to Create/Modify**:
- `backend/app/routes/check.py`
- `backend/app/main.py` — Add route

**Flow**:
1. Validate request (site_url, telegram_id)
2. Check rate limit
3. Save CheckRequest to DB
4. Run all 6 checks in parallel (`asyncio.gather`)
5. Build report
6. Save CheckResult to DB
7. Return JSON

**Reference**: [api/contracts.md](./api/contracts.md)

**Acceptance Criteria**:
- ✅ Test passes (GREEN)
- ✅ All 6 checks run
- ✅ Database saves records
- ✅ Returns correct JSON structure

**Dependencies**: TASK-019

---

### TASK-021: [TEST] API - Rate Limiting
**Type**: `[TEST]`  
**Time**: 20 min  
**Status**: ⏳

**Description**: Write test for rate limit (5/hour).

**Test Case**: 6 requests in quick succession → 6th returns 429

**Acceptance Criteria**:
- ✅ Test written
- ✅ Test fails (RED)

**Dependencies**: TASK-020

---

### TASK-022: [IMPL] Rate Limiting
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement rate limiting logic.

**Implementation**:
- Query: `SELECT COUNT(*) WHERE telegram_id = ? AND created_at > NOW() - INTERVAL '1 hour'`
- If >= 5, return 429

**Acceptance Criteria**:
- ✅ Test passes (GREEN)
- ✅ Returns 429 with retry_after_sec

**Dependencies**: TASK-021

---

### TASK-023: [TEST] API - Error Handling
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write tests for error cases.

**Test Cases**:
1. Invalid URL → 400
2. Site unreachable → 200 (partial report)
3. Timeout → 504

**Acceptance Criteria**:
- ✅ 3 tests written
- ✅ Tests fail (RED)

**Dependencies**: TASK-022

---

### TASK-024: [IMPL] Error Handling
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement error handling.

**Implementation**:
- URL validation
- Graceful degradation (continue if 1 check fails)
- Timeout handling (120 sec total)

**Acceptance Criteria**:
- ✅ All error tests pass (GREEN)
- ✅ Proper error responses

**Dependencies**: TASK-023

---

### TASK-025: [IMPL] Health Endpoint
**Type**: `[IMPL]`  
**Time**: 15 min  
**Status**: ⏳

**Description**: Add GET /api/health endpoint.

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "checks": {
    "database": "ok"
  }
}
```

**Acceptance Criteria**:
- ✅ Endpoint returns 200
- ✅ Can check DB connection

**Dependencies**: TASK-024

---

## Module 5: Telegram Bot (4-5 hours)

### TASK-026: [CONFIG] Bot Setup
**Type**: `[CONFIG]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Initialize bot with python-telegram-bot.

**Files to Create**:
- `telegram-bot/bot.py` — Main entry point
- `telegram-bot/.env.example`

**bot.py** (basic structure):
```python
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
```

**Commands**:
```bash
cd telegram-bot/
export BOT_TOKEN="your_token"
python bot.py
```

**Acceptance Criteria**:
- ✅ Bot starts without errors
- ✅ Responds to /start command
- ✅ Environment variables loaded

**Dependencies**: TASK-002

---

### TASK-027: [TEST] Start Handler with Deep Link
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write tests for /start handler.

**Files to Create**:
- `telegram-bot/tests/test_handlers.py`

**Test Cases**:
1. /start without args → welcome message
2. /start check_URL → parse URL, call API

**Acceptance Criteria**:
- ✅ 2 tests written
- ✅ Tests fail (RED)

**Dependencies**: TASK-026

---

### TASK-028: [IMPL] Start Handler
**Type**: `[IMPL]`  
**Time**: 1.5 hours  
**Status**: ⏳

**Description**: Implement /start handler with deep link parsing.

**Files to Create**:
- `telegram-bot/handlers/start.py`

**Flow**:
1. Parse args: `["check_aHR0cHM6Ly9leGFtcGxlLnJ1"]`
2. Decode Base64 → site_url
3. Send "⏳ Проверяю сайт..."
4. Call API
5. Format report
6. Send to user

**Reference**: [telegram/bot-logic.md](./telegram/bot-logic.md)

**Acceptance Criteria**:
- ✅ Tests pass (GREEN)
- ✅ Deep link parsed correctly
- ✅ Sends "checking" message

**Dependencies**: TASK-027

---

### TASK-029: [TEST] API Client
**Type**: `[TEST]`  
**Time**: 20 min  
**Status**: ⏳

**Description**: Write tests for API client.

**Files to Create**:
- `telegram-bot/tests/test_api_client.py`

**Test Cases**:
1. Successful response → return report
2. 429 rate limit → return error
3. Timeout → return error

**Acceptance Criteria**:
- ✅ 3 tests written
- ✅ Tests fail (RED)

**Dependencies**: TASK-028

---

### TASK-030: [IMPL] API Client
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement API client for Backend.

**Files to Create**:
- `telegram-bot/services/api_client.py`

**Methods**:
```python
async def check_site(site_url: str, telegram_id: int) -> dict:
    """Call Backend API to check site."""
    ...
```

**Retry Logic**:
- 500 error → retry once
- 429, 400 → no retry

**Acceptance Criteria**:
- ✅ Tests pass (GREEN)
- ✅ Retry logic works

**Dependencies**: TASK-029

---

### TASK-031: [TEST] Report Formatter
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Write tests for report formatting.

**Files to Create**:
- `telegram-bot/tests/test_formatter.py`

**Test Cases**:
1. High score (8+) → 🟢 emoji
2. Low score (<5) → 🔴 emoji
3. Format includes all sections

**Acceptance Criteria**:
- ✅ 3 tests written
- ✅ Tests fail (RED)

**Dependencies**: TASK-030

---

### TASK-032: [IMPL] Report Formatter
**Type**: `[IMPL]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Implement report formatting for Telegram.

**Files to Create**:
- `telegram-bot/services/formatter.py`

**Function**:
```python
def format_report(report: dict) -> str:
    """Convert API response to Telegram Markdown."""
    ...
```

**Reference**: [telegram/bot-logic.md#report-formatting](./telegram/bot-logic.md#report-formatting)

**Acceptance Criteria**:
- ✅ Tests pass (GREEN)
- ✅ Correct emoji based on score
- ✅ Personalized CTA

**Dependencies**: TASK-031

---

### TASK-033: [IMPL] Help Handler
**Type**: `[IMPL]`  
**Time**: 15 min  
**Status**: ⏳

**Description**: Add /help command.

**Files to Create**:
- `telegram-bot/handlers/help.py`

**Response**: Static help message

**Acceptance Criteria**:
- ✅ /help responds correctly

**Dependencies**: TASK-032

---

## Module 6: Integration & E2E Tests (3-4 hours)

### TASK-034: [TEST] Full Flow Integration
**Type**: `[TEST]`  
**Time**: 1.5 hours  
**Status**: ⏳

**Description**: Write integration test for complete flow.

**Files to Create**:
- `backend/tests/integration/test_full_flow.py`

**Test Cases**:
1. Good SEO site → score > 7
2. Bad SEO site → score < 5
3. Partial results (some checks fail)

**Acceptance Criteria**:
- ✅ 3 tests written
- ✅ Tests use test database
- ✅ Tests run all 6 checks

**Dependencies**: TASK-025, TASK-033

---

### TASK-035: [TEST] E2E with Real Sites
**Type**: `[TEST]`  
**Time**: 1.5 hours  
**Status**: ⏳

**Description**: Write E2E tests with real sites.

**Files to Create**:
- `backend/tests/e2e/test_real_sites.py`

**Test Cases**:
1. updates.idalite.ru → expect good score
2. Test site with known SEO issues → expect low score

**Mark**: `@pytest.mark.e2e`

**Acceptance Criteria**:
- ✅ 2 E2E tests written
- ✅ Tests use real HTTP (no mocks)
- ✅ Tests marked with @pytest.mark.e2e

**Dependencies**: TASK-034

---

### TASK-036: [REFACTOR] Code Coverage
**Type**: `[REFACTOR]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Ensure 80%+ test coverage.

**Commands**:
```bash
cd backend/
pytest --cov=app --cov-report=html --cov-report=term-missing
open htmlcov/index.html
```

**Tasks**:
- Identify uncovered lines
- Add missing tests
- Refactor if needed

**Acceptance Criteria**:
- ✅ Coverage > 80%
- ✅ All critical paths covered

**Dependencies**: TASK-035

---

## Module 7: Deployment (2-3 hours)

### TASK-037: [CONFIG] Railway - Backend
**Type**: `[CONFIG]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Deploy Backend API to Railway.

**Steps**:
1. Create Railway project
2. Add PostgreSQL database
3. Add Backend service
4. Configure env vars (DATABASE_URL)
5. Deploy

**Files to Create**:
- `backend/Dockerfile`
- `backend/.dockerignore`

**Acceptance Criteria**:
- ✅ Backend deployed
- ✅ Health endpoint accessible
- ✅ Database connected

**Dependencies**: TASK-036

---

### TASK-038: [CONFIG] Railway - Bot
**Type**: `[CONFIG]`  
**Time**: 45 min  
**Status**: ⏳

**Description**: Deploy Telegram Bot to Railway.

**Steps**:
1. Add Bot service to Railway project
2. Configure env vars (BOT_TOKEN, API_URL)
3. Deploy

**Files to Create**:
- `telegram-bot/Dockerfile`

**Acceptance Criteria**:
- ✅ Bot deployed
- ✅ Bot responding to /start

**Dependencies**: TASK-037

---

### TASK-039: [TEST] Smoke Tests (Production)
**Type**: `[TEST]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Run smoke tests in production.

**Tests**:
1. Send test request via Telegram
2. Verify report received
3. Check database has records
4. Check logs in Railway

**Acceptance Criteria**:
- ✅ At least 1 successful check in production
- ✅ No errors in logs

**Dependencies**: TASK-038

---

### TASK-040: [CONFIG] Monitoring Setup
**Type**: `[CONFIG]`  
**Time**: 30 min  
**Status**: ⏳

**Description**: Setup basic monitoring.

**Tools**:
- Railway logs (built-in)
- Sentry (optional)

**Acceptance Criteria**:
- ✅ Can view logs in Railway
- ✅ Error tracking configured (optional)

**Dependencies**: TASK-039

---

## Module 8: Documentation & Polish (1-2 hours)

### TASK-041: [CONFIG] Update Documentation
**Type**: `[CONFIG]`  
**Time**: 45 min  
**Status**: ⏳

**Description**: Update project documentation.

**Files to Update**:
- `README.md` — Installation, usage
- `backend/README.md` — API docs
- `telegram-bot/README.md` — Bot setup
- `.env.example` files

**Acceptance Criteria**:
- ✅ Clear installation instructions
- ✅ Environment variables documented
- ✅ API endpoints documented

**Dependencies**: TASK-040

---

### TASK-042: [REFACTOR] Final Polish
**Type**: `[REFACTOR]`  
**Time**: 1 hour  
**Status**: ⏳

**Description**: Final code cleanup and improvements.

**Tasks**:
- Run linters (ruff, mypy)
- Fix any warnings
- Add missing docstrings
- Code review (self)

**Acceptance Criteria**:
- ✅ No linter errors
- ✅ All public functions have docstrings
- ✅ Code follows conventions

**Dependencies**: TASK-041

---

## Summary

**Total Tasks**: 42  
**Total Time**: 25-32 hours  
**Timeline**: 10 days (2.5-3.5 hours/day)

### Task Distribution

| Module | Tasks | Time |
|--------|-------|------|
| 1. Setup | 4 tasks | 2-3h |
| 2. Checks | 12 tasks | 8-10h |
| 3. Report | 2 tasks | 2h |
| 4. API | 7 tasks | 4-5h |
| 5. Bot | 8 tasks | 4-5h |
| 6. Tests | 3 tasks | 3-4h |
| 7. Deploy | 4 tasks | 2-3h |
| 8. Docs | 2 tasks | 1-2h |

### Critical Path

```
TASK-001 → TASK-002 → TASK-003 → TASK-004
    ↓
TASK-005 → TASK-006 (Robots)
    ↓
TASK-007 → TASK-008 (Sitemap)
    ↓
TASK-009 → TASK-010 (Analytics)
    ↓
TASK-011 → TASK-012 (Noindex)
    ↓
TASK-013 → TASK-014 (Meta)
    ↓
TASK-015 → TASK-016 (Headings)
    ↓
TASK-017 → TASK-018 (Report)
    ↓
TASK-019 → TASK-020 → TASK-021 → TASK-022 (API)
    ↓
TASK-023 → TASK-024 → TASK-025
    ↓
TASK-026 → TASK-027 → TASK-028 → ... → TASK-033 (Bot)
    ↓
TASK-034 → TASK-035 → TASK-036 (Tests)
    ↓
TASK-037 → TASK-038 → TASK-039 → TASK-040 (Deploy)
    ↓
TASK-041 → TASK-042 (Polish)
```

---

## Next Steps

1. **Review this task list**
2. **Start with TASK-001**: Initialize project structure
3. **Follow TDD**: Always write tests before implementation
4. **Track progress**: Update status as tasks complete
5. **Daily target**: 3-4 tasks/day

---

## Task Tracking Template

Copy this to track progress:

```markdown
## Day 1 (Date: ____)
- [ ] TASK-001: Initialize project structure
- [ ] TASK-002: Setup dependencies
- [ ] TASK-003: Configure linters
- [ ] TASK-004: Setup database schema

## Day 2 (Date: ____)
- [ ] TASK-005: [TEST] Robots.txt
- [ ] TASK-006: [IMPL] Robots.txt
- [ ] TASK-007: [TEST] Sitemap.xml
- [ ] TASK-008: [IMPL] Sitemap.xml
```

---

**Status**: ✅ Ready for Implementation  
**Next**: Begin TASK-001
