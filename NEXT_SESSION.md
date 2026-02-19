# Промпт для следующей сессии: SEO Checker (Planning Complete)

## Статус проекта

**Фаза**: Planning Complete → Ready for Tasks  
**Локация**: `/Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool`  
**Дата**: 2026-02-18

---

## ✅ Что сделано

### 1. Спецификация (полная)
- 13 потенциальных проверок описаны
- Архитектура определена
- User stories написаны

### 2. Clarify (все вопросы отвечены)
- **MVP решён**: 6 проверок (не 13)
- **Без Playwright** (без FCP)
- **Без LLM** (без AI-проверок)
- PostgreSQL на Railway
- TDD обязателен (80% coverage)

### 3. Рефакторинг (модульная структура)
- Разбили 925 строк на 11 файлов
- Средний размер: 345 строк (отлично для AI)
- Навигация через README.md
- Все документы связаны

### 4. Plan (детальный план)
- 7 модулей с задачами
- Timeline: 25-32 часа (10 дней)
- Зависимости определены
- Интерфейсы описаны

---

## 📂 Структура specs (модульная)

```
specs/001-seo-checker/
├── README.md                    # 📚 START HERE
├── SPECIFICATION.md             # Executive Summary
├── CLARIFY.md                   # ✅ Ответы на вопросы
├── PLAN.md                      # ✅ План реализации
├── STATUS.md                    # Текущий статус
│
├── architecture/
│   ├── overview.md              # Компоненты, tech stack
│   └── data-flow.md             # Диаграммы, последовательности
│
├── checks/
│   ├── README.md                # Обзор проверок
│   └── mvp-checks.md            # 6 проверок (детально)
│
├── api/contracts.md             # API контракты
├── database/schema.md           # PostgreSQL schema
├── telegram/bot-logic.md        # Bot handlers
└── testing/strategy.md          # TDD стратегия
```

---

## 🎯 MVP Scope (финальный)

### Включено (6 checks)
1. Robots.txt
2. Sitemap.xml
3. Noindex on main page
4. Meta tags (title/description)
5. H1/H2 headings
6. Analytics counters

### Исключено (v1.1)
- FCP (Playwright)
- LLM checks (filters, local SEO)
- Schema.org, canonical, HTML sitemap, OpenGraph

---

## ⏭️ Следующий шаг: `/tasks`

**Задача**: Создать детальный task breakdown

Нужно создать `specs/001-seo-checker/TASKS.md`:

```
TASKS.md
├── Module 1: Setup (3-4 tasks)
│   ├── TASK-001: Initialize project structure
│   ├── TASK-002: Setup database schema
│   └── TASK-003: Configure linters
│
├── Module 2: Checks (12 tasks — 2 per check)
│   ├── TASK-004: [TEST] Robots.txt check
│   ├── TASK-005: [IMPL] Robots.txt check
│   ├── TASK-006: [TEST] Sitemap.xml check
│   ├── TASK-007: [IMPL] Sitemap.xml check
│   ... (6 checks × 2 tasks = 12 tasks)
│
├── Module 3: Report Builder (4 tasks)
├── Module 4: Backend API (6 tasks)
├── Module 5: Telegram Bot (5 tasks)
├── Module 6: Tests (3 tasks)
└── Module 7: Deployment (3 tasks)

TOTAL: ~40 tasks
```

Каждая задача должна иметь:
- **ID**: TASK-XXX
- **Type**: [TEST] / [IMPL] / [CONFIG]
- **Description**: Что делать
- **Files**: Какие файлы создать/изменить
- **Dependencies**: Какие задачи должны быть выполнены до этой
- **Time**: Оценка времени
- **Acceptance Criteria**: Как понять, что готово

---

## 🚀 Промпт для новой сессии

```
Продолжаем работу над SEO Checker MVP.

Локация: /Users/aleksejsermazko/Documents/Cursor/work/git/blog/SEO/seo-checker-tool

Статус:
- ✅ Спецификация готова
- ✅ Clarify завершён (MVP scope определён)
- ✅ План готов (PLAN.md)
- ⏸️ Сейчас нужно создать /tasks

Задача:
1. Прочитай specs/001-seo-checker/PLAN.md
2. Создай specs/001-seo-checker/TASKS.md
3. Разбей 7 модулей на ~40 конкретных задач
4. Каждая задача: ID, Type, Files, Dependencies, Time, Acceptance

Используем SpecifyX workflow + TDD (тесты перед реализацией).

Готов начать?
```

---

## 📖 Файлы для чтения в новой сессии

**Обязательно**:
1. `specs/001-seo-checker/README.md` — навигация
2. `specs/001-seo-checker/PLAN.md` — план реализации
3. `specs/001-seo-checker/STATUS.md` — текущий статус

**По необходимости** (при создании tasks):
- `specs/001-seo-checker/checks/mvp-checks.md` — детали проверок
- `specs/001-seo-checker/testing/strategy.md` — TDD подход
- `specs/001-seo-checker/api/contracts.md` — API контракты

---

## 🔑 Ключевые файлы проекта

| Файл | Строк | Назначение |
|------|-------|-----------|
| PLAN.md | 600+ | Детальный план реализации (7 модулей) |
| checks/mvp-checks.md | 542 | Спецификации 6 проверок с примерами |
| architecture/data-flow.md | 488 | Диаграммы потоков данных |
| api/contracts.md | 460 | API request/response schemas |
| database/schema.md | 462 | PostgreSQL schema, миграции |
| telegram/bot-logic.md | 570 | Bot handlers, форматирование |
| testing/strategy.md | 417 | TDD workflow, fixtures |

---

## ⏱️ Timeline

**Target**: 10 дней (25-32 часа)

| День | Модуль | Задачи |
|------|--------|--------|
| 1-2 | Setup + Checks 1-3 | Project structure, DB, first 3 checks |
| 3-4 | Checks 4-6 + Report | Last 3 checks, report builder |
| 5-6 | Backend API | FastAPI endpoint, DB integration |
| 7 | Telegram Bot | Handlers, formatting |
| 8 | Tests | Integration, E2E |
| 9 | Deployment | Railway setup |
| 10 | Buffer | Fixes, polish |

---

**Готово к следующему этапу!** 🎯
