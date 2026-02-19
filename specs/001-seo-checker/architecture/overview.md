# Architecture Overview

**Module**: Architecture  
**Last Updated**: 2026-02-18

---

## System Architecture

```
┌─────────────────┐
│   Web Form      │ (GitHub Pages / Static)
│   HTML/CSS/JS   │
└────────┬────────┘
         │ 1. User enters URL
         │ 2. Opens t.me/bot?start=check_ENCODED_URL
         ↓
┌─────────────────┐
│  Telegram Bot   │ (Railway - Container 1)
│  Python 3.11+   │
│  python-telegram-bot
└────────┬────────┘
         │ 3. /start check_URL
         │ 4. POST /api/check {site_url, telegram_id}
         ↓
┌─────────────────┐
│  Backend API    │ (Railway - Container 2)
│  FastAPI        │
│  BeautifulSoup  │
└────────┬────────┘
         │ 5. Run 6-8 checks (async)
         │ 6. Build report
         ↓
┌─────────────────┐
│  PostgreSQL     │ (Railway - Managed DB)
│  Database       │
└─────────────────┘
```

---

## Component Summary

### 1. Web Form (Frontend)
**Repository**: Same repo, `frontend/` folder  
**Deployment**: GitHub Pages or Netlify  
**Technology**: Vanilla HTML/CSS/JS

**Key Features**:
- Input field for site URL
- Client-side validation
- Generate Telegram deep link
- Open deep link in new tab

**Non-Goals**:
- No backend logic
- No authentication
- No data storage

---

### 2. Telegram Bot
**Repository**: Same repo, `telegram-bot/` folder  
**Deployment**: Railway (separate service)  
**Technology**: Python 3.11+, python-telegram-bot 20.7

**Key Features**:
- Handle `/start` command
- Parse deep link parameters
- Call Backend API
- Format and send report
- Log requests to database

**Non-Goals**:
- No SEO checks logic (delegated to backend)
- No complex conversation flows
- No user settings/preferences

---

### 3. Backend API
**Repository**: Same repo, `backend/` folder  
**Deployment**: Railway (separate service)  
**Technology**: Python 3.11+, FastAPI, BeautifulSoup

**Key Features**:
- REST API endpoint: `POST /api/check`
- Run 6-8 SEO checks asynchronously
- Aggregate results into report
- Calculate score
- Handle timeouts and errors
- Save results to database

**MVP Checks**:
1. Robots.txt check
2. Sitemap.xml check
3. Noindex check (main page)
4. Meta tags check (title/description)
5. Headings check (H1/H2)
6. Analytics check (counters)
7. HTML sitemap check (optional)
8. OpenGraph check (optional)

**Non-Goals** (v1.1+):
- No Playwright (FCP check)
- No LLM calls (filter pages, local SEO)
- No Schema.org validation
- No canonical checks

---

### 4. Database
**Technology**: PostgreSQL 14+  
**Deployment**: Railway managed database  
**Size**: Start with smallest tier (~$5/month)

**Key Tables**:
- `check_requests` — User requests
- `check_results` — Reports (JSONB)

See [database/schema.md](../database/schema.md) for details.

---

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Web Framework**: FastAPI 0.109+
- **HTTP Client**: httpx (async)
- **HTML Parser**: BeautifulSoup4
- **DB ORM**: SQLAlchemy 2.0
- **Async**: asyncio, aiohttp

### Telegram Bot
- **Library**: python-telegram-bot 20.7
- **Async**: Built-in async support

### Frontend
- **Core**: Vanilla HTML5/CSS3/JS (ES6+)
- **No frameworks**: Keep it simple

### Infrastructure
- **Hosting**: Railway (both bot & API)
- **Database**: Railway PostgreSQL
- **CI/CD**: GitHub Actions (optional)
- **Monitoring**: Railway logs + Sentry (optional)

---

## Deployment Architecture

### Development
```
Local Machine
├── Backend: localhost:8000
├── Bot: polling mode
└── DB: Docker PostgreSQL
```

### Production
```
Railway Project "seo-checker"
├── Service 1: telegram-bot
│   └── Env: BOT_TOKEN, API_URL, DATABASE_URL
├── Service 2: backend-api
│   └── Env: DATABASE_URL
└── Database: PostgreSQL (managed)
    └── Automatic backups
```

---

## Security Considerations

### API Security
- **No authentication** (public tool)
- **Rate limiting**: 5 checks/hour per IP (handled in backend)
- **CORS**: Limited to frontend domain
- **HTTPS only**: Enforced by Railway
- **Secrets**: Environment variables (not in code)

### Database Security
- **Minimal data**: Only telegram_id, site_url, report
- **No PII**: No names, emails, phone numbers
- **Retention**: Delete records > 90 days old
- **Access**: Only backend service can connect

### Bot Security
- **Webhook**: Use HTTPS webhook (not polling in production)
- **Token**: Store in env variable
- **Commands**: Validate deep link format
- **Rate limiting**: 5 checks/hour per telegram_id

---

## Scalability Plan

### Phase 1: MVP (0-100 checks/day)
- Single Railway instance for bot + API
- Smallest PostgreSQL tier
- No caching
- No queue

**Cost**: ~$15-20/month

### Phase 2: Growth (100-1000 checks/day)
- Separate bot & API services
- Add Redis for rate limiting
- Add queue (Celery + Redis)
- Scale to 2-3 API workers

**Cost**: ~$40-60/month

### Phase 3: Scale (1000+ checks/day)
- Horizontal scaling (multiple API workers)
- Database read replicas
- CDN for frontend
- Advanced monitoring

**Cost**: ~$100+/month

**MVP focuses on Phase 1 only.**

---

## Performance Targets

| Metric | Target | Measured By |
|--------|--------|-------------|
| Total check time | < 60 sec (90% of cases) | Backend logs |
| API response time | < 2 sec (excluding checks) | FastAPI middleware |
| Database query time | < 100 ms | SQLAlchemy logs |
| Bot message delivery | < 5 sec after API response | Telegram API |
| Uptime | > 99% | Railway metrics |

---

## Error Handling Strategy

### Levels
1. **Check-level**: Individual check fails → continue with others
2. **API-level**: Timeout (120 sec) → return partial report
3. **Bot-level**: API unreachable → retry once, then show error
4. **User-level**: Invalid URL → immediate validation error

### Error Recovery
- **Transient errors**: Retry with exponential backoff (max 2 retries)
- **Permanent errors**: Fail fast, log to Sentry
- **Partial failures**: Return what we have + mark failed checks

See [api/error-handling.md](../api/error-handling.md) for details.

---

## Data Flow

See [architecture/data-flow.md](./data-flow.md) for detailed sequence diagrams.

---

## Next Steps

1. Review this architecture
2. Read [components.md](./components.md) for detailed specs
3. Proceed to [checks/mvp-checks.md](../checks/mvp-checks.md)
4. Create implementation plan in `/plan`

---

**Related Documents**:
- [Data Flow](./data-flow.md)
- [Components Details](./components.md)
- [API Contracts](../api/contracts.md)
- [Database Schema](../database/schema.md)
