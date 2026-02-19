# Implementation Plan: SEO Checker MVP

**Spec ID**: 001-seo-checker  
**Phase**: Plan  
**Created**: 2026-02-18  
**Status**: Ready for Implementation

> **Navigation**: See [README.md](./README.md) for full documentation structure.

---

## 1. Overview

This plan breaks down the MVP implementation into **concrete modules and tasks** following TDD methodology.

### MVP Scope
- **6 checks** (robots, sitemap, noindex, meta, headings, analytics)
- Backend API (FastAPI)
- Telegram Bot
- PostgreSQL database
- No Playwright, no LLM
- Target: 1-2 weeks (20-27 hours)

### Implementation Strategy
- **TDD Required**: Tests first, then implementation
- **Bottom-up**: Core checks → API → Bot
- **Parallel work possible**: Backend + Bot can be developed separately after contracts are defined

---

## 2. Module Breakdown

### Module 1: Project Setup (2-3 hours)
**Description**: Initialize project structure, dependencies, tooling

**Tasks**:
1. Create project structure (backend/, telegram-bot/, tests/)
2. Setup Python virtual environments
3. Install dependencies (FastAPI, python-telegram-bot, pytest, etc.)
4. Configure linters (ruff, mypy)
5. Setup pre-commit hooks
6. Create base database connection
7. Run first migration (schema from [database/schema.md](./database/schema.md))

**Deliverables**:
- ✅ Working dev environment
- ✅ Database schema created
- ✅ Linters configured
- ✅ First "hello world" test passing

**Dependencies**: None

---

### Module 2: Core Check Engine (8-10 hours)
**Description**: Implement 6 MVP checks with TDD

**Order of Implementation** (simplest → complex):

#### 2.1. Robots.txt Check (1.5 hours)
- **Test**: `tests/unit/checks/test_robots_txt.py`
- **Implementation**: `backend/app/checks/robots_txt.py`
- **Test cases**: valid, missing sitemap, 404, timeout
- **See**: [checks/mvp-checks.md](./checks/mvp-checks.md#check-1-robotstxt)

#### 2.2. Sitemap.xml Check (1.5 hours)
- **Test**: `tests/unit/checks/test_sitemap_xml.py`
- **Implementation**: `backend/app/checks/sitemap_xml.py`
- **Test cases**: valid sitemap, sitemap index, invalid XML, 404
- **See**: [checks/mvp-checks.md](./checks/mvp-checks.md#check-2-sitemapxml)

#### 2.3. Analytics Check (1 hour)
- **Test**: `tests/unit/checks/test_analytics.py`
- **Implementation**: `backend/app/checks/analytics.py`
- **Test cases**: Yandex only, Google only, both, none
- **See**: [checks/mvp-checks.md](./checks/mvp-checks.md#check-6-analytics-counters)

#### 2.4. Noindex Check (1.5 hours)
- **Test**: `tests/unit/checks/test_noindex.py`
- **Implementation**: `backend/app/checks/noindex.py`
- **Test cases**: no noindex, noindex found, X-Robots-Tag header
- **See**: [checks/mvp-checks.md](./checks/mvp-checks.md#check-3-noindex-on-main-page)

#### 2.5. Meta Tags Check (1.5 hours)
- **Test**: `tests/unit/checks/test_meta_tags.py`
- **Implementation**: `backend/app/checks/meta_tags.py`
- **Test cases**: optimal, too short, too long, missing
- **See**: [checks/mvp-checks.md](./checks/mvp-checks.md#check-4-meta-tags-title--description)

#### 2.6. Headings Check (1 hour)
- **Test**: `tests/unit/checks/test_headings.py`
- **Implementation**: `backend/app/checks/headings.py`
- **Test cases**: perfect, no H1, multiple H1, no H2
- **See**: [checks/mvp-checks.md](./checks/mvp-checks.md#check-5-h1h2-structure)

**Shared Infrastructure**:
- `backend/app/checks/base.py` — CheckResult dataclass, base types
- `backend/app/checks/__init__.py` — Export all checks

**Deliverables**:
- ✅ 6 check functions implemented
- ✅ All unit tests passing (24+ tests)
- ✅ Coverage > 80% for checks module
- ✅ Type hints + docstrings

**Dependencies**: Module 1 (project setup)

---

### Module 3: Report Builder (2 hours)
**Description**: Aggregate check results into structured report

**Components**:

#### 3.1. Score Calculator
- **Test**: `tests/unit/test_report_builder.py::test_calculate_score`
- **Implementation**: `backend/app/report_builder.py::calculate_score()`
- **Formula**: `(ok_count * 1.0 + partial_count * 0.5) / total * 10`

#### 3.2. Category Grouper
- **Test**: `tests/unit/test_report_builder.py::test_group_by_category`
- **Implementation**: `backend/app/report_builder.py::group_by_category()`
- **Categories**: Technical (4), Content (2)

#### 3.3. Priority Extractor
- **Test**: `tests/unit/test_report_builder.py::test_extract_priorities`
- **Implementation**: `backend/app/report_builder.py::extract_top_priorities()`
- **Logic**: Sort by severity (critical > important), take top 3

#### 3.4. Report Builder (main)
- **Test**: `tests/unit/test_report_builder.py::test_build_report`
- **Implementation**: `backend/app/report_builder.py::build_report()`
- **Output**: Full JSON report matching [api/contracts.md](./api/contracts.md)

**Deliverables**:
- ✅ Report builder with 100% coverage
- ✅ Correct score calculation
- ✅ Proper category grouping

**Dependencies**: Module 2 (checks implemented)

---

### Module 4: Backend API (4-5 hours)
**Description**: FastAPI endpoint to run checks and return reports

**Components**:

#### 4.1. Database Models (1 hour)
- **Implementation**: `backend/app/models.py`
- **Models**: CheckRequest, CheckResult (SQLAlchemy)
- **See**: [database/schema.md](./database/schema.md)
- **Test**: Basic CRUD operations

#### 4.2. API Endpoint (2 hours)
- **Test**: `tests/integration/test_api_check_endpoint.py`
- **Implementation**: `backend/app/routes/check.py`
- **Endpoint**: `POST /api/check`
- **Flow**:
  1. Validate request (site_url, telegram_id)
  2. Check rate limit (5/hour)
  3. Save CheckRequest to DB
  4. Run all 6 checks in parallel (asyncio.gather)
  5. Build report
  6. Save CheckResult to DB
  7. Return JSON

**Validation**:
- site_url: must be valid HTTPS URL, not localhost/private IP
- telegram_id: positive integer

**Rate Limiting**:
- Query: `SELECT COUNT(*) WHERE telegram_id = ? AND created_at > NOW() - INTERVAL '1 hour'`
- If >= 5, return 429

#### 4.3. Error Handling (1 hour)
- **Test**: `tests/integration/test_api_errors.py`
- **Cases**: validation error, rate limit, site unreachable, timeout
- **See**: [api/contracts.md](./api/contracts.md#error-codes)

#### 4.4. Health Endpoint
- **Implementation**: `GET /api/health`
- **Response**: `{"status": "ok", "version": "1.0.0"}`

**Deliverables**:
- ✅ Working API endpoint
- ✅ Database integration
- ✅ Rate limiting working
- ✅ Error handling tested
- ✅ Integration tests passing

**Dependencies**: Module 2 (checks), Module 3 (report builder)

---

### Module 5: Telegram Bot (4-5 hours)
**Description**: Bot to receive deep links and send reports

**Components**:

#### 5.1. Bot Setup (1 hour)
- **Implementation**: `telegram-bot/bot.py`
- **Library**: python-telegram-bot 20.7
- **Config**: Read BOT_TOKEN, API_URL from env
- **Mode**: Polling (dev), Webhook (production)

#### 5.2. Handlers (2 hours)

##### /start Handler
- **Test**: `tests/unit/test_handlers.py::test_start_with_check`
- **Implementation**: `telegram-bot/handlers/start.py`
- **Flow**:
  1. Parse args: `["check_aHR0cHM6Ly9leGFtcGxlLnJ1"]`
  2. Decode Base64 → site_url
  3. Send "⏳ Проверяю сайт..."
  4. Call API: `POST /api/check`
  5. Format report
  6. Send to user

##### /help Handler
- **Implementation**: `telegram-bot/handlers/help.py`
- **Response**: Static help message

#### 5.3. API Client (1 hour)
- **Test**: `tests/unit/test_api_client.py`
- **Implementation**: `telegram-bot/services/api_client.py`
- **Methods**:
  - `check_site(site_url, telegram_id)` → report JSON
  - Handle retries (1 retry for 500, no retry for 429/400)

#### 5.4. Report Formatter (1 hour)
- **Test**: `tests/unit/test_formatter.py`
- **Implementation**: `telegram-bot/services/formatter.py`
- **Function**: `format_report(report_json)` → Telegram Markdown
- **Logic**: See [telegram/bot-logic.md](./telegram/bot-logic.md#report-formatting)

**Deliverables**:
- ✅ Working bot (polling mode)
- ✅ Deep link parsing
- ✅ Report formatting
- ✅ Error messages
- ✅ Unit tests passing

**Dependencies**: Module 4 (API ready)

---

### Module 6: Integration & E2E Tests (3-4 hours)
**Description**: Test full flow and edge cases

#### 6.1. Integration Tests (2 hours)
- **Test**: `tests/integration/test_full_flow.py`
- **Cases**:
  - Happy path: good SEO site
  - Partial results: mixed SEO
  - All failures: bad SEO site
  - Timeout handling
  - Database persistence

#### 6.2. E2E Tests (1-2 hours)
- **Test**: `tests/e2e/test_real_sites.py`
- **Cases**:
  - Real site with good SEO (e.g., updates.idalite.ru)
  - Real site with problems
  - Slow site (timeout test)
- **Note**: Mark with `@pytest.mark.e2e`, run separately

#### 6.3. Load Testing (optional, 1 hour)
- **Tool**: locust or wrk
- **Scenario**: 10 concurrent users, 50 requests
- **Goal**: Verify no crashes under load

**Deliverables**:
- ✅ Integration tests passing
- ✅ E2E tests passing (at least 2 real sites)
- ✅ Overall coverage > 80%

**Dependencies**: Module 4 (API), Module 5 (Bot)

---

### Module 7: Deployment (2-3 hours)
**Description**: Deploy to Railway

#### 7.1. Railway Configuration (1 hour)
- Create Railway project
- Add PostgreSQL database
- Add Backend service (FastAPI)
- Add Bot service (python-telegram-bot)
- Configure environment variables:
  - `DATABASE_URL`
  - `BOT_TOKEN`
  - `API_URL`

#### 7.2. Dockerfile (Backend)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7.3. Dockerfile (Bot)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

#### 7.4. Database Migration
- Run initial migration on Railway
- Verify tables created

#### 7.5. Smoke Tests (1 hour)
- Send test request via Telegram
- Verify report received
- Check logs in Railway
- Verify database has records

**Deliverables**:
- ✅ Backend deployed and accessible
- ✅ Bot running and responding
- ✅ Database connected
- ✅ Logs visible
- ✅ At least 1 successful check in production

**Dependencies**: All modules complete

---

## 3. Implementation Order

```
┌─────────────────────────────────────────────────────────────┐
│ Week 1                                                       │
├─────────────────────────────────────────────────────────────┤
│ Day 1-2: Module 1 (Setup) + Module 2.1-2.3 (First 3 checks)│
│ Day 3-4: Module 2.4-2.6 (Last 3 checks) + Module 3 (Report)│
│ Day 5-6: Module 4 (Backend API)                             │
│ Day 7:   Module 5 (Telegram Bot)                            │
├─────────────────────────────────────────────────────────────┤
│ Week 2                                                       │
├─────────────────────────────────────────────────────────────┤
│ Day 8:   Module 6 (Integration & E2E tests)                 │
│ Day 9:   Module 7 (Deployment)                              │
│ Day 10:  Buffer (fixes, polish)                             │
└─────────────────────────────────────────────────────────────┘
```

**Critical Path**: Module 1 → Module 2 → Module 3 → Module 4 → Module 5 → Module 7

**Parallel opportunities**:
- Module 5 (Bot) can start once Module 4 (API) has contracts defined (after 4.2)
- Tests can be written in parallel with implementation (TDD)

---

## 4. Dependencies Graph

```
Module 1 (Setup)
    ↓
Module 2 (Checks)
    ↓
Module 3 (Report Builder)
    ↓
Module 4 (Backend API) ←───┐
    ↓                      │
Module 5 (Telegram Bot) ────┘
    ↓
Module 6 (Tests)
    ↓
Module 7 (Deployment)
```

---

## 5. Interfaces Between Components

### 5.1. Check → Report Builder

**Input**: List of CheckResult
```python
CheckResult = {
    "id": str,
    "name": str,
    "status": "ok" | "partial" | "problem" | "error",
    "message": str,
    "severity": "critical" | "important" | "enhancement" | None,
    "category": str
}
```

**Output**: Report JSON (see [api/contracts.md](./api/contracts.md))

---

### 5.2. Backend API → Bot

**Request** (Bot → API):
```json
POST /api/check
{
  "site_url": "https://example.ru",
  "telegram_id": 123456789
}
```

**Response** (API → Bot):
```json
{
  "score": 7.5,
  "problems_critical": 1,
  "problems_important": 1,
  "checks_ok": 4,
  "categories": [...],
  "top_priorities": [...],
  "detailed_checks": [...]
}
```

**Error Response**:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "...",
    "retry_after_sec": 1380
  }
}
```

---

### 5.3. Bot → Telegram

**Input**: Report JSON (from API)

**Output**: Telegram Markdown message
```markdown
🟢 SEO-скор: 7.5/10

━━━━━━━━━━━━━━━━

📊 Результаты:
❌ Критичные проблемы: 1
⚠️ Важные: 1
✅ Всё хорошо: 4

...
```

---

## 6. Testing Strategy

### Unit Tests
- **Coverage target**: 80% minimum
- **Location**: `tests/unit/`
- **Mocking**: httpx.AsyncClient, database queries
- **Run**: `pytest tests/unit/ --cov=app`

### Integration Tests
- **Location**: `tests/integration/`
- **Database**: Test database (SQLite or PostgreSQL)
- **Run**: `pytest tests/integration/`

### E2E Tests
- **Location**: `tests/e2e/`
- **Mark**: `@pytest.mark.e2e`
- **Run**: `pytest tests/e2e/ -m e2e`
- **Note**: Slower, run less frequently

**See**: [testing/strategy.md](./testing/strategy.md) for details.

---

## 7. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Site unreachable during check | High | Medium | Return partial results, mark check as "error" |
| Rate limit abuse | Medium | Low | Implement 5/hour limit per telegram_id |
| Database connection issues | Low | High | Retry logic, connection pooling |
| Railway deployment issues | Low | Medium | Test locally first, use Railway logs |
| Tests taking too long | Medium | Low | Mock HTTP calls in unit tests, run E2E separately |

---

## 8. Environment Setup

### Development

**Backend**:
```bash
cd backend/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Database (local PostgreSQL or Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev postgres:14

# Run migrations
python -m alembic upgrade head

# Run API
uvicorn app.main:app --reload
```

**Bot**:
```bash
cd telegram-bot/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set env vars
export BOT_TOKEN="your_token"
export API_URL="http://localhost:8000"

# Run bot
python bot.py
```

**Tests**:
```bash
cd backend/
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

### Production (Railway)

**Environment Variables**:
- `DATABASE_URL` — Auto-set by Railway
- `BOT_TOKEN` — Telegram bot token
- `API_URL` — Backend API URL (e.g., `https://api-seo-checker.up.railway.app`)
- `ENVIRONMENT` — `production`

---

## 9. File Structure

```
seo-checker-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── database.py            # DB connection
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── check.py           # POST /api/check endpoint
│   │   ├── checks/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # CheckResult dataclass
│   │   │   ├── robots_txt.py
│   │   │   ├── sitemap_xml.py
│   │   │   ├── noindex.py
│   │   │   ├── meta_tags.py
│   │   │   ├── headings.py
│   │   │   └── analytics.py
│   │   ├── report_builder.py      # Build report from checks
│   │   └── validators.py          # URL validation
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py            # Fixtures
│   │   ├── unit/
│   │   │   ├── checks/
│   │   │   │   ├── test_robots_txt.py
│   │   │   │   ├── test_sitemap_xml.py
│   │   │   │   ├── test_noindex.py
│   │   │   │   ├── test_meta_tags.py
│   │   │   │   ├── test_headings.py
│   │   │   │   └── test_analytics.py
│   │   │   └── test_report_builder.py
│   │   ├── integration/
│   │   │   ├── test_api_check_endpoint.py
│   │   │   └── test_api_errors.py
│   │   └── e2e/
│   │       └── test_real_sites.py
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── telegram-bot/
│   ├── bot.py                     # Main entry point
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py               # /start handler
│   │   └── help.py                # /help handler
│   ├── services/
│   │   ├── api_client.py          # Backend API client
│   │   └── formatter.py           # Report formatting
│   ├── tests/
│   │   ├── test_handlers.py
│   │   ├── test_api_client.py
│   │   └── test_formatter.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                      # Already exists
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── docs/                          # Already exists
│   ├── checks-specification-v2-final.md
│   └── TELEGRAM_BOT_SETUP.md
│
└── specs/001-seo-checker/         # This specification
    ├── README.md
    ├── SPECIFICATION.md
    ├── CLARIFY.md
    ├── PLAN.md                    # 👈 This file
    └── ... (other modules)
```

---

## 10. Definition of Done

### Per Module
- [ ] All tests passing (unit + integration)
- [ ] Test coverage > 80% for that module
- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] Linting clean (ruff, mypy)
- [ ] Code reviewed (self-review at minimum)

### Overall MVP
- [ ] All 6 checks implemented and tested
- [ ] API endpoint working with all error cases handled
- [ ] Bot sending formatted reports
- [ ] Rate limiting working
- [ ] Deployed to Railway
- [ ] Smoke test in production passed
- [ ] Documentation updated (if needed)

---

## 11. Next Steps

### Immediate (Next Phase: `/tasks`)
1. Break down each module into **concrete tasks** with:
   - Task ID (e.g., `TASK-001`)
   - Description
   - Test file path
   - Implementation file path
   - Estimated time
   - Dependencies
2. Create task list for TDD implementation
3. Begin implementation: Module 1 (Project Setup)

### After Implementation
1. Launch MVP
2. Monitor for 1 week (collect feedback)
3. Plan v1.1 features:
   - Add Playwright (FCP check)
   - Add LLM checks (filters, local SEO)
   - Add `/history` command
   - Add HTML sitemap + OpenGraph checks

---

## 12. Timeline Summary

| Module | Tasks | Time | Cumulative |
|--------|-------|------|------------|
| 1. Setup | Project structure, DB, linters | 2-3h | 2-3h |
| 2. Checks | 6 checks with TDD | 8-10h | 10-13h |
| 3. Report Builder | Aggregation, scoring | 2h | 12-15h |
| 4. Backend API | FastAPI, DB integration | 4-5h | 16-20h |
| 5. Telegram Bot | Handlers, formatting | 4-5h | 20-25h |
| 6. Tests | Integration, E2E | 3-4h | 23-29h |
| 7. Deployment | Railway setup | 2-3h | 25-32h |
| **TOTAL MVP** | | **25-32 hours** | |

**Target**: 10 days (2.5-3.5 hours/day) or **1-2 weeks** full-time

---

## 13. Success Metrics

### Technical
- [ ] All tests passing (100% success rate)
- [ ] Coverage > 80%
- [ ] API response time < 60 sec (90% of requests)
- [ ] Zero crashes in first week
- [ ] Uptime > 99%

### Business
- [ ] 10+ checks completed in first week
- [ ] Average score: Track to understand baseline
- [ ] At least 1 conversion to Ida.Lite (inquiry/demo)

---

**Plan Status**: ✅ Ready for `/tasks`

**Next Step**: Create detailed task breakdown in `TASKS.md`
