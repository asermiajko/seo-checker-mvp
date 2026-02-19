# Database Schema

**Module**: Database  
**Technology**: PostgreSQL 14+  
**Last Updated**: 2026-02-18

---

## Overview

The database stores:
1. **Check requests** — User-initiated checks
2. **Check results** — SEO reports (JSONB)

**Design Principles**:
- Minimal data (only what's needed)
- No PII (no names, emails)
- JSONB for flexible report storage
- Indexes for common queries
- Automatic cleanup (90-day retention)

---

## Tables

### 1. check_requests

**Purpose**: Track all check requests from users.

```sql
CREATE TABLE check_requests (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    username VARCHAR(255),
    site_url VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_check_requests_telegram_id ON check_requests(telegram_id);
CREATE INDEX idx_check_requests_created_at ON check_requests(created_at DESC);
CREATE INDEX idx_check_requests_status ON check_requests(status);

-- Comments
COMMENT ON TABLE check_requests IS 'User-initiated SEO check requests';
COMMENT ON COLUMN check_requests.status IS 'pending, processing, completed, failed';
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | NO | Primary key |
| `telegram_id` | BIGINT | NO | Telegram user ID |
| `username` | VARCHAR(255) | YES | Telegram username (optional) |
| `site_url` | VARCHAR(500) | NO | Site being checked |
| `status` | VARCHAR(50) | NO | pending, processing, completed, failed |
| `created_at` | TIMESTAMP | NO | When request was created |
| `updated_at` | TIMESTAMP | NO | Last status update |

**Status Values**:
- `pending`: Request received, not yet processed
- `processing`: Currently running checks
- `completed`: Checks completed successfully
- `failed`: Checks failed (timeout, error)

---

### 2. check_results

**Purpose**: Store SEO check results.

```sql
CREATE TABLE check_results (
    id SERIAL PRIMARY KEY,
    check_request_id INTEGER NOT NULL REFERENCES check_requests(id) ON DELETE CASCADE,
    score DECIMAL(3, 1) NOT NULL,
    problems_critical INTEGER DEFAULT 0,
    problems_important INTEGER DEFAULT 0,
    checks_ok INTEGER DEFAULT 0,
    report_data JSONB NOT NULL,
    detailed_checks JSONB NOT NULL,
    processing_time_sec INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_check_results_request_id ON check_results(check_request_id);
CREATE INDEX idx_check_results_score ON check_results(score);
CREATE INDEX idx_check_results_created_at ON check_results(created_at DESC);

-- JSONB indexes (for querying report_data)
CREATE INDEX idx_check_results_report_data ON check_results USING GIN (report_data);

-- Comments
COMMENT ON TABLE check_results IS 'SEO check results and reports';
COMMENT ON COLUMN check_results.report_data IS 'Full report JSON (categories, priorities)';
COMMENT ON COLUMN check_results.detailed_checks IS 'All check results as JSON array';
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | NO | Primary key |
| `check_request_id` | INTEGER | NO | FK to check_requests |
| `score` | DECIMAL(3,1) | NO | Overall score (0.0 - 10.0) |
| `problems_critical` | INTEGER | NO | Count of critical problems |
| `problems_important` | INTEGER | NO | Count of important problems |
| `checks_ok` | INTEGER | NO | Count of successful checks |
| `report_data` | JSONB | NO | Full report (categories, top_priorities) |
| `detailed_checks` | JSONB | NO | Array of all check results |
| `processing_time_sec` | INTEGER | YES | How long checks took |
| `created_at` | TIMESTAMP | NO | When result was saved |

**JSONB Structure for `report_data`**:
```json
{
  "categories": [
    {
      "name": "Техническая база",
      "score": 4,
      "total": 5,
      "checks": ["tech-robots", "tech-sitemap"]
    }
  ],
  "top_priorities": [
    {
      "severity": "critical",
      "title": "...",
      "action": "...",
      "check_id": "tech-noindex"
    }
  ],
  "metadata": {
    "checked_at": "2026-02-18T15:30:00Z",
    "checks_total": 8,
    "checks_completed": 8,
    "checks_failed": 0
  }
}
```

**JSONB Structure for `detailed_checks`**:
```json
[
  {
    "id": "tech-robots",
    "name": "Robots.txt",
    "status": "ok",
    "message": "✅ Файл найден",
    "category": "technical"
  },
  {
    "id": "tech-noindex",
    "name": "Noindex Check",
    "status": "problem",
    "message": "❌ Noindex на главной",
    "severity": "critical",
    "category": "technical"
  }
]
```

---

## Relationships

```
check_requests (1) ──< (1) check_results
     id                check_request_id
```

- One `check_request` has exactly one `check_result` (1:1)
- If request is deleted, result is also deleted (CASCADE)

---

## Queries

### 1. Create Check Request

```sql
INSERT INTO check_requests (telegram_id, username, site_url, status)
VALUES (123456789, 'username', 'https://example.ru', 'pending')
RETURNING id;
```

### 2. Update Status

```sql
UPDATE check_requests
SET status = 'completed', updated_at = NOW()
WHERE id = 42;
```

### 3. Save Check Result

```sql
INSERT INTO check_results (
    check_request_id,
    score,
    problems_critical,
    problems_important,
    checks_ok,
    report_data,
    detailed_checks,
    processing_time_sec
)
VALUES (
    42,
    7.5,
    2,
    1,
    5,
    '{"categories": [...], "top_priorities": [...]}'::jsonb,
    '[{"id": "tech-robots", ...}]'::jsonb,
    23
);
```

### 4. Check Rate Limit

```sql
SELECT COUNT(*)
FROM check_requests
WHERE telegram_id = 123456789
  AND created_at > NOW() - INTERVAL '1 hour';
```

**Result**:
- If `COUNT >= 5`, reject request (rate limit exceeded)

### 5. Get User History (v1.1)

```sql
SELECT
    cr.site_url,
    cr.created_at,
    res.score,
    res.problems_critical,
    res.problems_important
FROM check_requests cr
LEFT JOIN check_results res ON res.check_request_id = cr.id
WHERE cr.telegram_id = 123456789
  AND cr.status = 'completed'
ORDER BY cr.created_at DESC
LIMIT 10;
```

### 6. Get Top Problematic Sites (Analytics)

```sql
SELECT
    cr.site_url,
    AVG(res.score) as avg_score,
    COUNT(*) as check_count
FROM check_requests cr
JOIN check_results res ON res.check_request_id = cr.id
GROUP BY cr.site_url
HAVING COUNT(*) > 1
ORDER BY avg_score ASC
LIMIT 20;
```

### 7. Get Most Common Problems (Analytics)

```sql
SELECT
    jsonb_array_elements(detailed_checks)->>'id' as check_id,
    jsonb_array_elements(detailed_checks)->>'status' as status,
    COUNT(*) as count
FROM check_results
WHERE jsonb_array_elements(detailed_checks)->>'status' = 'problem'
GROUP BY check_id, status
ORDER BY count DESC
LIMIT 10;
```

---

## Data Cleanup

**Policy**: Delete records older than 90 days.

**Cron Job** (runs daily):
```sql
DELETE FROM check_requests
WHERE created_at < NOW() - INTERVAL '90 days';
```

**Note**: `check_results` will be auto-deleted via CASCADE.

**Alternative**: Archive to S3 before deletion (for analytics).

---

## Migrations

### Migration 001: Initial Schema

```sql
-- File: backend/migrations/001_initial_schema.sql

BEGIN;

CREATE TABLE check_requests (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    username VARCHAR(255),
    site_url VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_check_requests_telegram_id ON check_requests(telegram_id);
CREATE INDEX idx_check_requests_created_at ON check_requests(created_at DESC);

CREATE TABLE check_results (
    id SERIAL PRIMARY KEY,
    check_request_id INTEGER NOT NULL REFERENCES check_requests(id) ON DELETE CASCADE,
    score DECIMAL(3, 1) NOT NULL,
    problems_critical INTEGER DEFAULT 0,
    problems_important INTEGER DEFAULT 0,
    checks_ok INTEGER DEFAULT 0,
    report_data JSONB NOT NULL,
    detailed_checks JSONB NOT NULL,
    processing_time_sec INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_check_results_request_id ON check_results(check_request_id);
CREATE INDEX idx_check_results_score ON check_results(score);

COMMIT;
```

**Run Migration**:
```bash
psql $DATABASE_URL -f backend/migrations/001_initial_schema.sql
```

---

## SQLAlchemy Models (Python)

```python
# backend/app/models.py
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
    
    # Relationship
    result = relationship("CheckResult", back_populates="request", uselist=False, cascade="all, delete-orphan")


class CheckResult(Base):
    __tablename__ = "check_results"
    
    id = Column(Integer, primary_key=True, index=True)
    check_request_id = Column(Integer, ForeignKey("check_requests.id", ondelete="CASCADE"), nullable=False)
    score = Column(DECIMAL(3, 1), nullable=False)
    problems_critical = Column(Integer, default=0)
    problems_important = Column(Integer, default=0)
    checks_ok = Column(Integer, default=0)
    report_data = Column(JSONB, nullable=False)
    detailed_checks = Column(JSONB, nullable=False)
    processing_time_sec = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Relationship
    request = relationship("CheckRequest", back_populates="result")
```

---

## Backup Strategy

**MVP**: Railway automatic backups (daily)

**Future**:
- Nightly backup to S3
- Point-in-time recovery (PITR)
- Backup retention: 30 days

---

## Performance Optimization

### Current (MVP)
- Indexes on `telegram_id`, `created_at`, `score`
- GIN index on JSONB for flexible queries
- Connection pooling (SQLAlchemy default)

### Future (if needed)
- Partitioning by date (`check_requests` table)
- Read replicas for analytics queries
- Materialized views for common aggregations

---

## Security

### Access Control
- **Backend API**: Full read/write access
- **Bot**: Read/write via API only (no direct DB access)
- **Admin**: Read-only dashboard (future)

### Data Privacy
- **No PII**: We don't store names, emails, phone numbers
- **Minimal data**: Only telegram_id, username, site_url
- **Retention**: 90 days (then deleted)

### Secrets
- Database credentials in environment variables
- Use Railway's managed secrets

---

## Next Steps

1. Review this schema
2. Create migration file
3. Implement SQLAlchemy models
4. Write database tests

---

**Related Documents**:
- [API Contracts](../api/contracts.md)
- [Architecture Overview](../architecture/overview.md)
- [Data Flow](../architecture/data-flow.md)
