# ✅ ИСПРАВЛЕНО: Telegram бот теперь показывает все 10 проверок

## Проблема:
Telegram бот не показывал проверки со статусом `"partial"`:
- **Headings** (H1/H2 структура) - status: "partial", severity: "enhancement"
- **Микроразметка Schema.org** - status: "partial", severity: "important"

## Причина:
Бот фильтровал проверки только по:
- `status == "problem"` + `severity == "critical"` → 🔴 Критичные
- `status == "problem"` + `severity == "important"` → 🟡 Важные
- `status == "ok"` → ✅ Всё хорошо

**Пропускал:** `status == "partial"` (частичные проблемы)

## Решение:
Обновлена логика в `telegram-bot/handlers/url.py`:

```python
# Было:
important_problems = [c for c in detailed_checks if c.get("status") == "problem" and c.get("severity") == "important"]

# Стало:
important_problems = [c for c in detailed_checks if c.get("severity") == "important" and c.get("status") in ["problem", "partial"]]

# Добавлена новая категория:
partial_checks = [c for c in detailed_checks if c.get("status") == "partial" and c.get("severity") not in ["critical", "important"]]
```

## Новый формат отчёта:
1. 🔴 **Критичные проблемы** (status: "problem", severity: "critical")
2. 🟡 **Важные проблемы** (status: "problem" ИЛИ "partial", severity: "important")
3. ⚠️ **Можно улучшить** (status: "partial", severity: "enhancement" или null)
4. ✅ **Всё хорошо** (status: "ok")

## Результат:
Теперь в отчёте будут отображаться ВСЕ 10 проверок:
- **Headings** → в секции "⚠️ Можно улучшить"
- **Микроразметка Schema.org** → в секции "🟡 Важные проблемы"

## Деплой:
- Commit: `6715fe6`
- Задеплоено на Railway (telegram-bot service)
- Статус: ✅ Готово

---

**Протестируйте заново через @site_SEO_cheker_bot - теперь все 10 проверок будут в отчёте!**
