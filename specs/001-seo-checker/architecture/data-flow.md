# Data Flow & Sequences

**Module**: Architecture  
**Last Updated**: 2026-02-18

---

## Complete User Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Opens https://checker.idalite.ru
     ↓
┌─────────────────┐
│   Web Form      │
│  (Frontend)     │
└────┬────────────┘
     │ 2. Enters: "https://example.ru"
     │ 3. Clicks "Проверить"
     │ 4. Form generates deep link:
     │    t.me/seo_checker_bot?start=check_aHR0cHM6Ly9leGFtcGxlLnJ1
     │ 5. Opens in new tab
     ↓
┌─────────────────┐
│   Telegram      │
│   (Mobile/Web)  │
└────┬────────────┘
     │ 6. User clicks "START" or bot opens automatically
     │ 7. Sends: /start check_aHR0cHM6Ly9leGFtcGxlLnJ1
     ↓
┌─────────────────┐
│  Telegram Bot   │
│   (Railway)     │
└────┬────────────┘
     │ 8. Parses command
     │ 9. Decodes URL: "https://example.ru"
     │ 10. Sends: "⏳ Проверяю сайт..."
     │ 11. POST /api/check
     │     Body: {
     │       "site_url": "https://example.ru",
     │       "telegram_id": 123456789
     │     }
     ↓
┌─────────────────┐
│  Backend API    │
│   (Railway)     │
└────┬────────────┘
     │ 12. Validates URL
     │ 13. Runs 6-8 checks in parallel (asyncio.gather)
     │ 14. Aggregates results
     │ 15. Calculates score
     │ 16. Saves to DB
     │ 17. Returns JSON report
     │     (15-45 seconds total)
     ↓
┌─────────────────┐
│  Telegram Bot   │
└────┬────────────┘
     │ 18. Receives JSON
     │ 19. Formats as Telegram message (Markdown)
     │ 20. Sends report to user
     ↓
┌─────────┐
│  User   │ Receives report with:
│         │ - Score: 7.5/10
│         │ - Categories breakdown
│         │ - Top-3 problems
│         │ - CTA to Ida.Lite
└─────────┘
```

---

## Detailed Sequence: Web Form → Bot

```
User                Frontend            Telegram            Bot
 │                      │                   │                │
 │  Enter URL          │                   │                │
 │─────────────────────>│                   │                │
 │                      │                   │                │
 │  Click "Проверить"  │                   │                │
 │─────────────────────>│                   │                │
 │                      │                   │                │
 │                      │ Validate URL      │                │
 │                      │────────┐          │                │
 │                      │        │          │                │
 │                      │<───────┘          │                │
 │                      │                   │                │
 │                      │ Encode URL        │                │
 │                      │────────┐          │                │
 │                      │        │          │                │
 │                      │<───────┘          │                │
 │                      │                   │                │
 │                      │ Generate deep link│                │
 │                      │ (t.me/bot?start=...)              │
 │                      │────────┐          │                │
 │                      │        │          │                │
 │                      │<───────┘          │                │
 │                      │                   │                │
 │  Open new tab       │                   │                │
 │<─────────────────────│                   │                │
 │                      │                   │                │
 │  Telegram opens with deep link           │                │
 │──────────────────────────────────────────>│                │
 │                                          │                │
 │  Click "START"                           │                │
 │──────────────────────────────────────────>│                │
 │                                          │                │
 │                                          │ /start cmd     │
 │                                          │───────────────>│
 │                                          │                │
```

---

## Detailed Sequence: Bot → Backend → Bot

```
Bot                 Backend API         Database           Checks
 │                      │                   │                │
 │ POST /api/check     │                   │                │
 │ {site_url, tg_id}  │                   │                │
 │─────────────────────>│                   │                │
 │                      │                   │                │
 │                      │ Validate request  │                │
 │                      │────────┐          │                │
 │                      │        │          │                │
 │                      │<───────┘          │                │
 │                      │                   │                │
 │                      │ Check rate limit  │                │
 │                      │──────────────────>│                │
 │                      │<──────────────────│                │
 │                      │                   │                │
 │                      │ Save check_request│                │
 │                      │──────────────────>│                │
 │                      │<──────────────────│                │
 │                      │                   │                │
 │                      │ Run checks (parallel)              │
 │                      │───────────────────────────────────>│
 │                      │                   │                │
 │                      │                   │  Check 1: robots.txt
 │                      │                   │  Check 2: sitemap.xml
 │                      │                   │  Check 3: noindex
 │                      │                   │  Check 4: meta tags
 │                      │                   │  Check 5: headings
 │                      │                   │  Check 6: analytics
 │                      │                   │                │
 │                      │<──────────────────────────────────│
 │                      │ Results: [...]    │                │
 │                      │                   │                │
 │                      │ Build report      │                │
 │                      │────────┐          │                │
 │                      │        │          │                │
 │                      │<───────┘          │                │
 │                      │                   │                │
 │                      │ Calculate score   │                │
 │                      │────────┐          │                │
 │                      │        │          │                │
 │                      │<───────┘          │                │
 │                      │                   │                │
 │                      │ Save check_result │                │
 │                      │──────────────────>│                │
 │                      │<──────────────────│                │
 │                      │                   │                │
 │ JSON Report         │                   │                │
 │<─────────────────────│                   │                │
 │                      │                   │                │
```

---

## Data Transformations

### 1. User Input → Deep Link

**Input**: 
```
https://example.ru
```

**Process**:
```javascript
// Frontend: script.js
const url = "https://example.ru";
const encoded = btoa(url); // Base64 encode
// encoded = "aHR0cHM6Ly9leGFtcGxlLnJ1"

const deepLink = `https://t.me/seo_checker_bot?start=check_${encoded}`;
// deepLink = "https://t.me/seo_checker_bot?start=check_aHR0cHM6Ly9leGFtcGxlLnJ1"
```

**Output**: Deep link

---

### 2. Deep Link → API Request

**Input**: 
```
/start check_aHR0cHM6Ly9leGFtcGxlLnJ1
```

**Process**:
```python
# Bot: handlers.py
def handle_start(update, context):
    args = context.args  # ["check_aHR0cHM6Ly9leGFtcGxlLnJ1"]
    if args and args[0].startswith("check_"):
        encoded = args[0].replace("check_", "")
        site_url = base64.b64decode(encoded).decode()  # "https://example.ru"
        
        telegram_id = update.effective_user.id  # 123456789
        
        # Call API
        api_request = {
            "site_url": site_url,
            "telegram_id": telegram_id
        }
```

**Output**: API request JSON

---

### 3. Checks Results → Report JSON

**Input**:
```python
checks_results = [
    {"id": "robots", "status": "ok", "message": "Файл найден", "severity": None},
    {"id": "sitemap", "status": "ok", "message": "Файл найден", "severity": None},
    {"id": "noindex", "status": "problem", "message": "Noindex на главной", "severity": "critical"},
    # ... more checks
]
```

**Process**:
```python
# Backend: report_builder.py
def build_report(checks_results):
    ok_count = sum(1 for c in checks_results if c["status"] == "ok")
    partial_count = sum(1 for c in checks_results if c["status"] == "partial")
    problem_count = sum(1 for c in checks_results if c["status"] == "problem")
    
    score = (ok_count * 1.0 + partial_count * 0.5) / len(checks_results) * 10
    
    critical = [c for c in checks_results if c["severity"] == "critical"]
    important = [c for c in checks_results if c["severity"] == "important"]
    
    return {
        "score": round(score, 1),
        "problems_critical": len(critical),
        "problems_important": len(important),
        "checks_ok": ok_count,
        "categories": group_by_category(checks_results),
        "top_priorities": critical[:3],
        "detailed_checks": checks_results
    }
```

**Output**: Report JSON (see [api/contracts.md](../api/contracts.md))

---

### 4. Report JSON → Telegram Message

**Input**:
```json
{
  "score": 6.5,
  "problems_critical": 2,
  "problems_important": 1,
  "checks_ok": 5,
  "top_priorities": [...]
}
```

**Process**:
```python
# Bot: formatters.py
def format_report(report):
    score = report["score"]
    emoji = "🔴" if score < 5 else "🟡" if score < 7 else "🟢"
    
    text = f"{emoji} **SEO-скор: {score}/10**\n\n"
    text += f"❌ Критичные проблемы: {report['problems_critical']}\n"
    text += f"⚠️ Важные: {report['problems_important']}\n"
    text += f"✅ Всё хорошо: {report['checks_ok']}\n\n"
    # ... format top_priorities
    return text
```

**Output**: Telegram Markdown message

---

## Timing Breakdown

| Stage | Duration | Notes |
|-------|----------|-------|
| Frontend: User input → Deep link | < 100ms | Instant |
| Telegram: Open → /start | 1-2 sec | User action |
| Bot: Parse → API call | < 500ms | Python processing |
| API: Validation | < 100ms | FastAPI |
| API: Run checks (parallel) | 10-40 sec | Depends on site speed |
| API: Build report | < 500ms | Python processing |
| API: Save to DB | < 200ms | PostgreSQL |
| Bot: Format → Send | < 1 sec | Telegram API |
| **TOTAL** | **15-45 sec** | Target: < 60 sec in 90% cases |

---

## Error Flow

### Scenario: Invalid URL

```
User → Frontend: "not-a-url"
Frontend: Client-side validation fails
User: Sees error message (no Telegram opened)
```

### Scenario: API Timeout

```
Bot → Backend: POST /api/check
Backend: Runs checks... (timeout after 120 sec)
Backend → Bot: 504 Gateway Timeout
Bot → User: "⚠️ Проверка заняла слишком много времени. Попробуйте позже."
```

### Scenario: Site Unreachable

```
Backend: Check 1 (robots.txt) → 404
Backend: Mark as "problem" but continue with other checks
Backend: Returns partial report
Bot → User: Shows results with note about unreachable resources
```

---

## Rate Limiting Flow

```
User → Bot → Backend: POST /api/check
Backend → Database: Check rate limit
  - Query: SELECT COUNT(*) FROM check_requests 
           WHERE telegram_id = ? 
           AND created_at > NOW() - INTERVAL '1 hour'
  - Result: 4 checks in last hour
  - Limit: 5 checks/hour
  - Status: ✅ ALLOW

Backend: Process request

---

(Same user tries 6th check)
Backend → Database: Check rate limit
  - Result: 5 checks in last hour
  - Status: ❌ DENY (429 Too Many Requests)

Backend → Bot: {"error": "rate_limit_exceeded"}
Bot → User: "⚠️ Вы достигли лимита проверок (5 в час). Попробуйте через X минут."
```

---

## Database Interaction Flow

### Writing Data

```
Backend API → PostgreSQL:

1. Insert check_request:
   INSERT INTO check_requests (telegram_id, username, site_url, status)
   VALUES (123456789, 'username', 'https://example.ru', 'pending')
   RETURNING id;
   
   Returns: check_request_id = 42

2. Run checks...

3. Update check_request status:
   UPDATE check_requests 
   SET status = 'completed', updated_at = NOW()
   WHERE id = 42;

4. Insert check_result:
   INSERT INTO check_results (check_request_id, score, report_data, ...)
   VALUES (42, 6.5, '{"categories": [...]}', ...);
```

### Reading Data (for /history command - v1.1)

```
Bot → Backend: GET /api/history?telegram_id=123456789

Backend → PostgreSQL:
   SELECT cr.*, res.*
   FROM check_requests cr
   LEFT JOIN check_results res ON res.check_request_id = cr.id
   WHERE cr.telegram_id = 123456789
   ORDER BY cr.created_at DESC
   LIMIT 10;

Backend → Bot: JSON array of past checks
```

---

## Next Steps

- Review [architecture/overview.md](./overview.md) for component details
- See [api/contracts.md](../api/contracts.md) for exact request/response formats
- See [database/schema.md](../database/schema.md) for table structures

---

**Related Documents**:
- [Architecture Overview](./overview.md)
- [API Contracts](../api/contracts.md)
- [Database Schema](../database/schema.md)
- [Error Handling](../api/error-handling.md)
