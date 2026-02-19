# API Contracts

**Module**: API  
**Last Updated**: 2026-02-18

---

## Overview

This document defines the REST API contracts between the Telegram Bot and Backend API.

**Base URL**: `https://api.seo-checker.idalite.ru` (production)  
**Protocol**: HTTPS only  
**Format**: JSON  
**Authentication**: None (public API)

---

## Endpoints

### 1. POST /api/check

**Description**: Run SEO checks for a site.

**Request**:
```json
{
  "site_url": "https://example.ru",
  "telegram_id": 123456789
}
```

**Request Schema**:
```typescript
{
  site_url: string;      // Required, must be valid HTTPS URL
  telegram_id: number;   // Required, Telegram user ID
}
```

**Validation Rules**:
- `site_url`:
  - Must start with `http://` or `https://`
  - Must not be `localhost` or private IP
  - Max length: 500 characters
- `telegram_id`:
  - Must be positive integer
  - Range: 1 to 2^63-1

**Response (Success)**:
```json
{
  "score": 7.5,
  "problems_critical": 2,
  "problems_important": 1,
  "checks_ok": 5,
  "categories": [
    {
      "name": "Техническая база",
      "score": 4,
      "total": 5,
      "checks": ["tech-robots", "tech-sitemap", "tech-noindex", "tech-analytics"]
    },
    {
      "name": "Контент",
      "score": 1,
      "total": 2,
      "checks": ["content-meta", "content-headings"]
    }
  ],
  "top_priorities": [
    {
      "severity": "critical",
      "title": "Главная страница закрыта от индексации",
      "action": "Удалите тег <meta name='robots' content='noindex'>",
      "check_id": "tech-noindex"
    },
    {
      "severity": "important",
      "title": "Title слишком короткий",
      "action": "Увеличьте длину до 30-65 символов",
      "check_id": "content-meta"
    }
  ],
  "detailed_checks": [
    {
      "id": "tech-robots",
      "name": "Robots.txt",
      "status": "ok",
      "message": "✅ Файл найден, содержит User-agent и Sitemap",
      "category": "technical"
    },
    {
      "id": "tech-noindex",
      "name": "Noindex Check",
      "status": "problem",
      "message": "❌ Главная страница закрыта от индексации",
      "severity": "critical",
      "category": "technical"
    }
  ],
  "metadata": {
    "checked_at": "2026-02-18T15:30:00Z",
    "processing_time_sec": 23,
    "checks_total": 8,
    "checks_completed": 8,
    "checks_failed": 0
  }
}
```

**Response Schema**:
```typescript
{
  score: number;                    // 0.0 to 10.0
  problems_critical: number;        // Count
  problems_important: number;       // Count
  checks_ok: number;                // Count
  categories: Category[];           // Grouped results
  top_priorities: Priority[];       // Top 3 critical/important
  detailed_checks: Check[];         // All check results
  metadata: Metadata;               // Processing info
}

type Category = {
  name: string;                     // Category name
  score: number;                    // Checks passed in category
  total: number;                    // Total checks in category
  checks: string[];                 // Check IDs
}

type Priority = {
  severity: "critical" | "important";
  title: string;                    // Short description
  action: string;                   // How to fix
  check_id: string;                 // Reference to detailed_checks
}

type Check = {
  id: string;                       // Unique check ID
  name: string;                     // Human-readable name
  status: "ok" | "partial" | "problem" | "error";
  message: string;                  // Result message (with emoji)
  severity?: "critical" | "important" | "enhancement"; // If status != ok
  category: "technical" | "content" | "structure" | "seo" | "social";
}

type Metadata = {
  checked_at: string;               // ISO 8601 timestamp
  processing_time_sec: number;      // How long it took
  checks_total: number;             // Total checks attempted
  checks_completed: number;         // Successfully completed
  checks_failed: number;            // Errored out
}
```

**Response (Error - Validation)**:
```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid site_url: must start with http:// or https://",
    "field": "site_url"
  }
}
```

**Response (Error - Rate Limit)**:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Вы превысили лимит проверок (5 в час). Попробуйте через 23 минуты.",
    "retry_after_sec": 1380
  }
}
```

**Response (Error - Timeout)**:
```json
{
  "error": {
    "code": "timeout",
    "message": "Проверка превысила лимит времени (120 сек)",
    "partial_results": {
      "score": 5.0,
      "checks_completed": 5,
      "checks_failed": 3
    }
  }
}
```

**HTTP Status Codes**:
- `200 OK`: Check completed successfully
- `400 Bad Request`: Invalid request (validation error)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `504 Gateway Timeout`: Check timeout

---

### 2. GET /api/health

**Description**: Health check endpoint.

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "api": "ok"
  },
  "uptime_sec": 86400
}
```

---

### 3. GET /api/history (v1.1)

**Description**: Get check history for a user.

**Query Params**:
- `telegram_id` (required): User's Telegram ID
- `limit` (optional): Max results (default: 10, max: 50)

**Response**:
```json
{
  "checks": [
    {
      "site_url": "https://example.ru",
      "score": 7.5,
      "checked_at": "2026-02-18T15:30:00Z",
      "report_id": "abc123"
    }
  ],
  "total": 15
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 400 | Invalid request parameters |
| `rate_limit_exceeded` | 429 | Too many requests |
| `site_unreachable` | 400 | Site is down or unreachable |
| `timeout` | 504 | Check took too long |
| `internal_error` | 500 | Server error |

---

## Rate Limiting

**Rule**: 5 checks per hour per `telegram_id`

**Headers** (in response):
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1708272600
```

**Implementation**:
- Store in PostgreSQL: `check_requests` table
- Query: `SELECT COUNT(*) WHERE telegram_id = ? AND created_at > NOW() - INTERVAL '1 hour'`
- If count >= 5, return 429

---

## Timeout Strategy

**Total timeout**: 120 seconds

**Per-check timeout**: 10 seconds

**Behavior**:
- If total time > 120 sec, stop remaining checks
- Return partial results with error code
- Mark incomplete checks as `"status": "error", "message": "Timeout"`

---

## Retry Logic (Client-Side)

**Bot should retry**:
- `500 Internal Server Error`: Retry once after 5 sec
- `504 Gateway Timeout`: Do NOT retry (already took 120 sec)
- Network errors: Retry once after 3 sec

**Bot should NOT retry**:
- `400 Bad Request`: Invalid input, no point
- `429 Too Many Requests`: User exceeded limit

---

## Example: Full Flow

### Step 1: Bot sends request

```bash
curl -X POST https://api.seo-checker.idalite.ru/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://example.ru",
    "telegram_id": 123456789
  }'
```

### Step 2: Backend processes

```
[15:30:00] API received request
[15:30:01] Validated URL
[15:30:01] Checked rate limit: OK (3/5)
[15:30:02] Saved check_request (id=42)
[15:30:02] Running 8 checks in parallel...
[15:30:15] Check 1 (robots.txt): OK
[15:30:15] Check 2 (sitemap.xml): OK
[15:30:16] Check 3 (noindex): PROBLEM (critical)
[15:30:17] Check 4 (meta): PARTIAL (important)
[15:30:17] Check 5 (headings): OK
[15:30:18] Check 6 (analytics): OK
[15:30:19] Check 7 (html sitemap): OK
[15:30:20] Check 8 (opengraph): PARTIAL
[15:30:21] Built report (score: 7.5)
[15:30:22] Saved check_result (id=87)
[15:30:22] Returning response (23 sec total)
```

### Step 3: Bot receives response

```json
{
  "score": 7.5,
  "problems_critical": 1,
  "problems_important": 1,
  "checks_ok": 5,
  "..."
}
```

### Step 4: Bot formats and sends to user

```
🟢 SEO-скор: 7.5/10

❌ Критичные проблемы: 1
⚠️ Важные: 1
✅ Всё хорошо: 5

━━━━━━━━━━━━━━━━

🚨 Топ проблемы:

1. ❌ Главная страница закрыта от индексации
   → Удалите тег <meta name='robots' content='noindex'>

2. ⚠️ Title слишком короткий
   → Увеличьте длину до 30-65 символов

━━━━━━━━━━━━━━━━

💡 Эти проблемы решаются в Ida.Lite!
👉 [Узнать больше]
```

---

## Security Considerations

### Input Validation
- **Always validate** `site_url` to prevent SSRF attacks
- Block private IPs: `127.0.0.1`, `10.x.x.x`, `192.168.x.x`, `localhost`
- Block file:// and other non-HTTP protocols

### Rate Limiting
- Implement per-telegram_id limits
- Consider IP-based limits as backup (if bot is abused)

### Error Messages
- Don't expose internal paths or stack traces
- Use generic messages like "Internal error occurred"

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API response time (excluding checks) | < 2 sec | FastAPI overhead |
| Total check time | 15-45 sec | 90% of requests < 60 sec |
| Database query time | < 100 ms | Save/retrieve operations |
| Concurrent requests | 5-10 | MVP capacity |

---

## Next Steps

1. Review this contract
2. Implement backend endpoint in `/plan`
3. Implement bot API client
4. Write integration tests

---

**Related Documents**:
- [Error Handling](./error-handling.md)
- [Architecture Overview](../architecture/overview.md)
- [Data Flow](../architecture/data-flow.md)
- [Database Schema](../database/schema.md)
