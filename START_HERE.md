# 🚀 SEO Checker MVP - Старт Разработки

**Статус**: Tasks Complete → Ready to Code  
**Дата**: 2026-02-18  
**Локация**: `/Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool`

---

## ✅ Планирование завершено!

Все этапы **SpecifyX workflow** пройдены:

1. ✅ `/specify` — Спецификация написана
2. ✅ `/clarify` — Все вопросы отвечены, MVP определён
3. ✅ **Рефакторинг** — Разбили спеку на модули
4. ✅ `/plan` — Детальный план из 7 модулей
5. ✅ `/tasks` — **42 конкретные задачи готовы**

---

## 📂 Навигация по документации

**Главный вход**: `specs/001-seo-checker/README.md`

### Основные документы
- **SPECIFICATION.md** — Executive Summary
- **CLARIFY.md** — Ответы на вопросы
- **PLAN.md** — План реализации (7 модулей, 25-32h)
- **TASKS.md** — 42 задачи с TDD 👈 **НАЧАТЬ ЗДЕСЬ**
- **STATUS.md** — Текущий статус

### Модули (детальные спеки)
- `architecture/` — Система, компоненты, data flow
- `checks/` — 6 проверок с примерами кода
- `api/` — API контракты
- `database/` — PostgreSQL schema
- `telegram/` — Bot handlers
- `testing/` — TDD стратегия

---

## 🎯 MVP Scope (финальный)

### Включено (6 checks)
1. ✅ Robots.txt
2. ✅ Sitemap.xml
3. ✅ Noindex on main page
4. ✅ Meta tags (title/description)
5. ✅ H1/H2 headings
6. ✅ Analytics counters

### Исключено (v1.1+)
- ❌ FCP Speed (Playwright)
- ❌ LLM checks
- ❌ Schema.org, canonical, HTML sitemap, OpenGraph

---

## 📋 42 Tasks Overview

| Module | Tasks | Time | First Task |
|--------|-------|------|-----------|
| 1. Setup | TASK-001 to 004 | 2-3h | Initialize structure |
| 2. Checks | TASK-005 to 016 | 8-10h | [TEST] Robots.txt |
| 3. Report | TASK-017 to 018 | 2h | [TEST] Score calc |
| 4. API | TASK-019 to 025 | 4-5h | [TEST] API endpoint |
| 5. Bot | TASK-026 to 033 | 4-5h | Bot setup |
| 6. Tests | TASK-034 to 036 | 3-4h | Integration tests |
| 7. Deploy | TASK-037 to 040 | 2-3h | Railway setup |
| 8. Docs | TASK-041 to 042 | 1-2h | Documentation |

**Total**: 25-32 hours (10 days @ 2.5-3.5h/day)

---

## 🏁 Как начать

### Шаг 1: Прочитай TASKS.md
```bash
cd /Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool
cat specs/001-seo-checker/TASKS.md
```

### Шаг 2: Начни с TASK-001
**TASK-001**: Initialize Project Structure (30 min)

```bash
# Создать структуру
mkdir -p backend/app/{routes,checks,utils}
mkdir -p backend/tests/{unit/checks,integration,e2e}
mkdir -p telegram-bot/{handlers,services,tests}

# Создать файлы
touch backend/app/__init__.py
touch backend/app/main.py
# ... и т.д.
```

### Шаг 3: Следуй TDD
Для каждой проверки:
1. **[TEST]** — Пиши тесты (RED)
2. **[IMPL]** — Реализация (GREEN)
3. **[REFACTOR]** — Улучшение (если нужно)

### Шаг 4: Отслеживай прогресс
Обновляй статус задач в TASKS.md:
- ⏳ Not Started
- 🔄 In Progress
- ✅ Completed

---

## 📖 Полезные ссылки

### Спецификации проверок (с примерами кода)
- [checks/mvp-checks.md](specs/001-seo-checker/checks/mvp-checks.md)

### API контракты (request/response)
- [api/contracts.md](specs/001-seo-checker/api/contracts.md)

### Database schema
- [database/schema.md](specs/001-seo-checker/database/schema.md)

### TDD стратегия
- [testing/strategy.md](specs/001-seo-checker/testing/strategy.md)

---

## 🔑 Ключевые решения

| Что | Решение | Причина |
|-----|---------|---------|
| MVP checks | 6 проверок | Быстрый launch |
| Playwright | Нет в MVP | Сложность |
| LLM | Нет в MVP | Стоимость |
| Database | PostgreSQL | Готов к росту |
| Hosting | Railway | Простота |
| TDD | Обязательно | Constitution |
| Coverage | 80% min | Constitution |
| Timeline | 10 дней | Fast feedback |

---

## ⚡ Quick Start Commands

```bash
# Перейти в проект
cd /Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool

# Читать задачи
cat specs/001-seo-checker/TASKS.md

# Создать структуру (TASK-001)
mkdir -p backend/app/{routes,checks,utils}
mkdir -p backend/tests/{unit/checks,integration,e2e}
mkdir -p telegram-bot/{handlers,services,tests}

# Setup virtual environments
cd backend/ && python -m venv .venv && source .venv/bin/activate
cd ../telegram-bot/ && python -m venv .venv && source .venv/bin/activate

# Install dependencies (after creating requirements.txt)
pip install -r requirements.txt
```

---

## 🎬 Промпт для AI Assistant

```
Начинаем реализацию SEO Checker MVP.

Локация: /Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool

Все планирование завершено:
- ✅ Спецификация готова (specs/001-seo-checker/)
- ✅ 42 задачи расписаны (TASKS.md)
- ✅ TDD workflow определён

Начинаем с TASK-001: Initialize Project Structure

Прочитай:
1. specs/001-seo-checker/TASKS.md (задача TASK-001)
2. specs/001-seo-checker/PLAN.md (для контекста)

Создай структуру проекта согласно TASK-001.

Готов начать?
```

---

## 📊 Прогресс трекинг

### Week 1
- [ ] Day 1: TASK-001 to 004 (Setup)
- [ ] Day 2: TASK-005 to 008 (Robots, Sitemap)
- [ ] Day 3: TASK-009 to 012 (Analytics, Noindex)
- [ ] Day 4: TASK-013 to 016 (Meta, Headings)
- [ ] Day 5: TASK-017 to 020 (Report, API)
- [ ] Day 6: TASK-021 to 025 (API errors)
- [ ] Day 7: TASK-026 to 030 (Bot)

### Week 2
- [ ] Day 8: TASK-031 to 036 (Bot + Tests)
- [ ] Day 9: TASK-037 to 040 (Deploy)
- [ ] Day 10: TASK-041 to 042 (Docs + Polish)

---

**Готово к разработке!** 🚀

**Следующий шаг**: Открой `specs/001-seo-checker/TASKS.md` и начни с TASK-001.
