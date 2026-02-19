# SEO Checker Specification - Navigation

**Spec ID**: 001-seo-checker  
**Status**: Clarify Phase → Planning  
**Last Updated**: 2026-02-18

---

## 📚 Documentation Structure

This specification is split into modular parts for easier navigation and maintenance. Each file is < 200 lines for optimal AI assistant performance.

---

## 🗺️ Quick Navigation

### 1. Main Documents
- **[SPECIFICATION.md](./SPECIFICATION.md)** — Executive summary, user stories, success criteria
- **[CLARIFY.md](./CLARIFY.md)** — ✅ Clarification questions & answers (ANSWERED)
- **[PLAN.md](./PLAN.md)** — ✅ Implementation plan (READY)
- **[TASKS.md](./TASKS.md)** — ✅ Task breakdown (42 tasks, READY)

### 2. Architecture
- **[architecture/overview.md](./architecture/overview.md)** — System architecture, components, tech stack
- **[architecture/data-flow.md](./architecture/data-flow.md)** — Data flow diagrams, sequences
- **[architecture/components.md](./architecture/components.md)** — Detailed component specifications

### 3. Checks (Core Logic)
- **[checks/README.md](./checks/README.md)** — Overview of all SEO checks
- **[checks/mvp-checks.md](./checks/mvp-checks.md)** — 6-8 checks for MVP (detailed specs)
- **[checks/future-checks.md](./checks/future-checks.md)** — Checks for v1.1+ (FCP, LLM, Schema.org)

### 4. API Contracts
- **[api/contracts.md](./api/contracts.md)** — Request/response schemas, validation rules
- **[api/error-handling.md](./api/error-handling.md)** — Error codes, retry logic, timeouts

### 5. Database
- **[database/schema.md](./database/schema.md)** — PostgreSQL schema, indexes, migrations

### 6. Telegram Bot
- **[telegram/bot-logic.md](./telegram/bot-logic.md)** — Bot handlers, message formatting, deep links

### 7. Testing
- **[testing/strategy.md](./testing/strategy.md)** — TDD approach, test coverage, tools
- **[testing/test-data.md](./testing/test-data.md)** — Test sites, mocks, fixtures

---

## 🎯 MVP Scope (Clarified)

After clarification phase, we decided on:

- **6-8 checks** (not full 13)
- **No Playwright** in MVP (defer FCP to v1.1)
- **No LLM** in MVP (defer filter/local checks to v1.1)
- **PostgreSQL** on Railway
- **Target**: 1-2 weeks for MVP launch

**MVP Checks:**
1. ✅ Robots.txt
2. ✅ Sitemap.xml
3. ✅ Noindex on main page
4. ✅ Title/Description length
5. ✅ H1/H2 structure
6. ✅ Analytics counters
7. ⚠️ HTML sitemap (optional for 8-check version)
8. ⚠️ OpenGraph tags (optional for 8-check version)

---

## 🔄 SpecifyX Workflow Status

- [x] `/specify` — Initial specification written
- [x] `/clarify` — Questions answered, decisions made
- [x] `/plan` — Implementation plan created
- [x] `/tasks` — Task breakdown created (42 tasks)
- [ ] `/analyze` — **NEXT**: Check dependencies (optional)
- [ ] `/implement` — TDD implementation

---

## 📖 Reading Order for Implementation

**For first-time readers:**
1. Start with [SPECIFICATION.md](./SPECIFICATION.md) (executive summary)
2. Review [CLARIFY.md](./CLARIFY.md) (understand decisions)
3. Read [architecture/overview.md](./architecture/overview.md) (understand system)
4. Continue to specific modules as needed

**For implementation:**
1. Read [PLAN.md](./PLAN.md) (when available)
2. Pick a task from `/tasks`
3. Read only relevant module (e.g., `checks/mvp-checks.md` for implementing a check)
4. Follow TDD: read [testing/strategy.md](./testing/strategy.md) first

---

## 🏗️ Project Structure

```
seo-checker-tool/
├── specs/001-seo-checker/          # This specification
│   ├── README.md                    # 👈 You are here
│   ├── SPECIFICATION.md             # Executive summary
│   ├── CLARIFY.md                   # Q&A
│   ├── PLAN.md                      # Implementation plan
│   ├── architecture/                # System design
│   ├── checks/                      # SEO checks specs
│   ├── api/                         # API contracts
│   ├── database/                    # DB schema
│   ├── telegram/                    # Bot logic
│   └── testing/                     # Test strategy
├── backend/                         # FastAPI (to be created)
├── telegram-bot/                    # Bot code (to be created)
├── frontend/                        # Web form (exists)
└── docs/                            # Additional docs
```

---

## 🔗 External References

- **Constitution**: `Ida.lite/.specify/memory/constitution.md` (TDD principles)
- **SpecifyX Workflow**: `.cursor/rules/specifyx-workflow.mdc`
- **Detailed Checks**: `docs/checks-specification-v2-final.md`
- **Telegram Setup**: `docs/TELEGRAM_BOT_SETUP.md`

---

## 💡 Tips for AI Assistants

- **Context Management**: Read only the specific module you need for current task
- **Navigation**: Always start from this README to find relevant documents
- **Linking**: Cross-reference using relative paths (e.g., `[checks](./checks/mvp-checks.md)`)
- **Updates**: When modifying specs, update the "Last Updated" date in this README

---

**Last Updated**: 2026-02-18  
**Next Review**: After `/plan` phase
