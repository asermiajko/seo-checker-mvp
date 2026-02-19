# SEO Checker - Executive Summary

**Spec ID**: 001-seo-checker  
**Status**: Clarified → Planning  
**Created**: 2026-02-18  
**Last Updated**: 2026-02-18  
**Author**: System  
**Reviewers**: @aleksejsermazko

> **📚 Full Documentation**: See [README.md](./README.md) for complete modular documentation.

---

## 1. Overview

### Problem Statement
Застройщики недвижимости теряют органический трафик из-за базовых ошибок в SEO-настройках сайтов. Существующие SEO-инструменты (Screaming Frog, Ahrefs) либо слишком сложны для маркетологов, либо дороги, либо не учитывают специфику недвижимости.

### Solution
Бесплатный SEO-чекер с автоматической проверкой **6-8 базовых параметров** (MVP), специфичных для сайтов застройщиков. Отчёт приходит в Telegram за 30-45 секунд.

### MVP Scope (After Clarification)
- **6-8 checks** (not full 13 — deferred complex ones to v1.1)
- **No Playwright** (no FCP speed check)
- **No LLM** (no AI-powered checks)
- **Simple & Fast**: HTTP + HTML parsing only
- **Target**: 1-2 weeks for MVP launch

### Success Criteria
- ✅ 100+ проверок в первый месяц
- ✅ Время проверки < 60 секунд в 90% случаев
- ✅ Accuracy проверок > 95% (валидация на 20 тестовых сайтах)
- ✅ 10+ лидов на Ida.Lite за 3 месяца
- ✅ Uptime > 99%

---

## 2. Quick Links

**For detailed specifications, see modular docs**:

- **Architecture**: [architecture/overview.md](./architecture/overview.md)
- **Data Flow**: [architecture/data-flow.md](./architecture/data-flow.md)
- **MVP Checks**: [checks/mvp-checks.md](./checks/mvp-checks.md) — **6-8 checks (detailed)**
- **Future Checks**: [checks/future-checks.md](./checks/future-checks.md) — v1.1 roadmap
- **API Contracts**: [api/contracts.md](./api/contracts.md)
- **Database Schema**: [database/schema.md](./database/schema.md)
- **Telegram Bot**: [telegram/bot-logic.md](./telegram/bot-logic.md)
- **Testing Strategy**: [testing/strategy.md](./testing/strategy.md)

---

## 3. User Stories

### US-1: Базовая проверка сайта
**Как** маркетолог застройщика  
**Я хочу** быстро проверить базовые SEO-настройки своего сайта  
**Чтобы** понять, какие проблемы нужно исправить в первую очередь

**Acceptance Criteria:**
- [ ] Могу ввести URL сайта в веб-форму
- [ ] Форма валидирует URL (https://)
- [ ] После отправки открывается Telegram-бот
- [ ] Бот отправляет отчёт в течение 60 секунд
- [ ] Отчёт содержит скор (X/10) и разбивку по категориям

### US-2: Детальный анализ проблем
**Как** маркетолог  
**Я хочу** увидеть конкретные проблемы и рекомендации  
**Чтобы** знать, что именно исправлять

**Acceptance Criteria:**
- [ ] Отчёт показывает топ-3 критичных проблемы
- [ ] Каждая проблема содержит: что это значит + как исправить
- [ ] Есть ссылка на Ida.Lite с предложением решения

### US-3: Сохранение истории проверок
**Как** маркетолог  
**Я хочу** видеть историю моих проверок  
**Чтобы** отслеживать прогресс улучшений

**Acceptance Criteria:**
- [ ] Бот сохраняет telegram_id и site_url
- [ ] Могу запросить `/history` и получить список проверок
- [ ] Вижу динамику скора (было 5/10 → стало 8/10)

### US-4: Admin Dashboard
**Как** admin  
**Я хочу** видеть статистику использования  
**Чтобы** понимать эффективность инструмента

**Acceptance Criteria:**
- [ ] Количество проверок/день
- [ ] Средний скор сайтов
- [ ] Топ-3 проблемы (чаще всего встречаются)
- [ ] Топ-10 доменов
- [ ] Конверсия: форма → бот → отчёт

---

## 4. Technical Stack (MVP)

**See [architecture/overview.md](./architecture/overview.md) for full details.**

### Components
1. **Web Form** (frontend/) — HTML/CSS/JS, GitHub Pages
2. **Telegram Bot** (telegram-bot/) — Python 3.11+, python-telegram-bot 20.7, Railway
3. **Backend API** (backend/) — Python 3.11+, FastAPI, BeautifulSoup, Railway
4. **Database** — PostgreSQL 14+ on Railway

### MVP Checks (6-8 total)
1. ✅ Robots.txt — Presence, User-agent, Sitemap
2. ✅ Sitemap.xml — Presence, validity, URL count
3. ✅ Noindex — No noindex on main page
4. ✅ Meta Tags — Title/Description length
5. ✅ Headings — H1/H2 structure
6. ✅ Analytics — Yandex.Metrika, Google Analytics
7. ⚠️ HTML Sitemap — Optional (for 8-check version)
8. ⚠️ OpenGraph — Optional (for 8-check version)

**See [checks/mvp-checks.md](./checks/mvp-checks.md) for detailed specs.**

### Deferred to v1.1+
- ❌ FCP Speed Check (Playwright)
- ❌ Filter Pages (LLM)
- ❌ Local SEO (LLM)
- ❌ Schema.org (slow, 15 pages)
- ❌ Canonical Tags (slow, 15 pages)

**See [checks/future-checks.md](./checks/future-checks.md) for v1.1 roadmap.**

---

## 5. Functional Requirements Summary

**See detailed modules for complete functional specs:**

- **Web Form**: Basic URL collection + Telegram deep link generation
- **Telegram Bot**: [telegram/bot-logic.md](./telegram/bot-logic.md)
- **Backend API**: [api/contracts.md](./api/contracts.md)
- **Individual Checks**: [checks/mvp-checks.md](./checks/mvp-checks.md)
- **Database**: [database/schema.md](./database/schema.md)

### Core Flow
1. User enters URL in web form
2. Form opens Telegram with deep link
3. Bot extracts URL, calls API
4. API runs 6-8 checks (parallel)
5. API builds report (score, categories, priorities)
6. Bot formats and sends report to user

---

## 6. Non-Functional Requirements

### Performance (MVP Targets)
- Total check time < 60 sec (90% of cases)
- API response < 2 sec (excluding checks)
- Database queries < 100 ms
- Individual check timeout: 10 sec

### Reliability
- Uptime > 99%
- Error rate < 5%
- Graceful degradation (partial results if some checks fail)

### Security
- Rate limiting: 5 checks/hour per telegram_id
- HTTPS only
- No PII stored
- Secrets in environment variables

### Maintainability (TDD Required)
- Test coverage > 80%
- Type hints mandatory
- Docstrings for all public functions
- Linting: ruff + mypy

**See [architecture/overview.md](./architecture/overview.md) for details.**

---

## 7. Data Contracts

**See detailed schemas in**:
- [api/contracts.md](./api/contracts.md) — API request/response formats
- [database/schema.md](./database/schema.md) — Database tables
- [architecture/data-flow.md](./architecture/data-flow.md) — Data transformations

---

## 8. Testing Requirements (TDD)

**See [testing/strategy.md](./testing/strategy.md) for complete strategy.**

### Approach
- **TDD Required**: Tests before implementation (RED → GREEN → REFACTOR)
- **Coverage Target**: 80% minimum
- **Test Pyramid**: 70% unit, 20% integration, 10% E2E

### Test Types
- Unit tests: Each check independently (mocked HTTP)
- Integration tests: Full API flow with test DB
- E2E tests: Real sites (good/bad SEO)

### Tools
- pytest, pytest-cov, pytest-asyncio
- httpx mocking for unit tests
- Test fixtures for HTML/XML/TXT samples

---

## 9. Deployment & Infrastructure

**Hosting**: Railway (bot + API + PostgreSQL)  
**Cost**: ~$15-20/month

### Environments
- **Development**: Local (Docker Compose optional)
- **Production**: Railway

### Monitoring
- Railway logs
- Sentry for errors (optional)
- Simple SQL analytics

**See [architecture/overview.md](./architecture/overview.md) for deployment details.**

---

## 10. Risks & Mitigations (MVP Focused)

| Risk | Impact | MVP Mitigation |
|------|--------|----------------|
| Site unreachable | Medium | Return partial results, continue other checks |
| Database full | Low | 90-day cleanup policy |
| Rate limit abuse | Medium | 5 checks/hour per telegram_id |
| Hosting costs | Low | Railway ~$15/month (manageable) |

---

## 11. MVP Timeline

**Target**: 1-2 weeks (8-12 hours implementation + 4-6 hours testing)

| Phase | Tasks | Time |
|-------|-------|------|
| **Phase 1: Core Checks** | 6 MVP checks (TDD) | 8-10 hours |
| **Phase 2: API + Bot** | Backend API + Telegram bot | 6-8 hours |
| **Phase 3: Testing** | Unit + Integration tests | 4-6 hours |
| **Phase 4: Deploy** | Railway setup | 2-3 hours |
| **TOTAL (MVP)** | | **20-27 hours** |

**Post-MVP (v1.1)**:
- Add Playwright (FCP check)
- Add LLM checks (filters, local SEO)
- Add Schema.org, canonical checks
- Estimated: +15-20 hours

---

## 12. Acceptance Criteria

### MVP Definition of Done
- [ ] All 6-8 MVP checks implemented with TDD
- [ ] Test coverage > 80%
- [ ] All tests passing (unit + integration + E2E)
- [ ] Deployed to Railway (bot + API + DB)
- [ ] Tested with 5 real sites (good/bad/mixed SEO)
- [ ] Rate limiting working (5 checks/hour)
- [ ] Error handling tested (timeout, unreachable, rate limit)
- [ ] Documentation complete (this spec + code docs)

### Sign-Off
- [ ] Product Owner: @aleksejsermazko

---

## Next Steps (SpecifyX Workflow)

1. ✅ `/specify` — Specification written
2. ✅ `/clarify` — Questions answered, MVP scope defined
3. ⏭️ **`/plan`** — Create detailed implementation plan (NEXT)
4. ⏭️ `/tasks` — Break down into TDD tasks
5. ⏭️ `/analyze` — Check dependencies
6. ⏭️ `/implement` — TDD implementation

---

## 📚 Full Documentation

This is an **executive summary**. For detailed specifications, see:

**[README.md](./README.md)** — Navigation to all modular docs

Key modules:
- [architecture/](./architecture/) — System design, data flow, components
- [checks/](./checks/) — MVP & future checks (detailed specs)
- [api/](./api/) — API contracts, error handling
- [database/](./database/) — Schema, queries, migrations
- [telegram/](./telegram/) — Bot logic, handlers, formatters
- [testing/](./testing/) — TDD strategy, fixtures, test data

---

**Last Updated**: 2026-02-18  
**Status**: Clarified → Ready for Planning
