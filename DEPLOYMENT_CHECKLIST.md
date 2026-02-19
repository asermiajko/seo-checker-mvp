# Quick Start: UTM Tracking Testing

## Перед деплоем

### 1. Применить миграцию (локально):

```bash
cd backend/
# Если есть виртуальное окружение с alembic:
alembic upgrade head

# Проверить:
# Должна появиться таблица web_sessions
```

### 2. Проверить изменения локально:

#### Backend:
```bash
cd backend/
uvicorn app.main:app --reload

# Проверить endpoints:
curl -X POST http://localhost:8000/api/track-session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "utm_source": "test",
    "utm_campaign": "local_testing"
  }'
```

#### Frontend:
```bash
cd frontend/
# Открыть index.html в браузере
# Проверить консоль при клике на кнопку
```

#### Telegram Bot:
```bash
cd telegram-bot/
export TELEGRAM_TOKEN="your_token"
export API_URL="http://localhost:8000"
python bot.py

# Открыть в Telegram:
# /start session_550e8400-e29b-41d4-a716-446655440000
```

---

## Деплой на Railway

### 1. Backend (применить миграцию на production):

```bash
cd backend/

# Вариант 1: через Railway CLI
railway run alembic upgrade head

# Вариант 2: через Python (если alembic не в PATH)
railway run python -m alembic upgrade head
```

**Важно**: Миграция должна пройти **до** деплоя нового кода!

### 2. Задеплоить код:

```bash
# Закоммитить изменения
git add .
git commit -m "feat: add UTM tracking and session attribution"
git push origin main

# Railway автоматически задеплоит:
# - backend (после миграции)
# - telegram-bot
# - frontend (если на Railway)
```

---

## Проверка после деплоя

### 1. Полный флоу с UTM:

```bash
# 1. Открыть landing с UTM:
https://your-landing.com/?utm_source=github&utm_medium=readme&utm_campaign=testing

# 2. Кликнуть "Открыть Telegram-бот"
# → Проверить Network tab в DevTools: POST /api/track-session (200 OK)

# 3. В Telegram:
# → Автоматически откроется /start session_UUID
# → Отправить URL: https://example.com
# → Получить отчёт

# 4. Проверить БД (через Railway CLI):
railway run psql -c "SELECT session_id, utm_source, telegram_id FROM web_sessions ORDER BY created_at DESC LIMIT 5;"
```

### 2. Прямой заход в бота (без веб-формы):

```bash
# Открыть бота: https://t.me/site_SEO_cheker_bot
# → /start
# → Отправить URL: https://example.com
# → Получить отчёт

# В БД session_id должен быть NULL (это норма)
```

---

## Rollback (если что-то пошло не так)

### Откатить миграцию:

```bash
cd backend/
railway run alembic downgrade -1
```

### Откатить код:

```bash
git revert HEAD
git push origin main
```

---

## Полезные команды для отладки

### Посмотреть последние сессии:

```bash
railway run psql -c "
SELECT 
  session_id,
  utm_source,
  utm_campaign,
  telegram_id,
  bot_started_at,
  created_at
FROM web_sessions
ORDER BY created_at DESC
LIMIT 10;
"
```

### Посмотреть связь сессий с проверками:

```bash
railway run psql -c "
SELECT 
  ws.session_id,
  ws.utm_source,
  ws.telegram_id,
  cr.site_url,
  cr.created_at as check_time
FROM web_sessions ws
LEFT JOIN check_requests cr ON ws.session_id = cr.session_id
WHERE ws.created_at > NOW() - INTERVAL '1 day'
ORDER BY ws.created_at DESC;
"
```

---

## Troubleshooting

### Проблема: Миграция не применяется

```bash
# Проверить текущую версию:
railway run alembic current

# Если показывает старую версию:
railway run alembic history
railway run alembic upgrade a1b2c3d4e5f6
```

### Проблема: Frontend не отправляет session_id

- Проверить консоль браузера (F12 → Console)
- Проверить Network tab: должен быть POST на /api/track-session
- Проверить CORS (должен быть разрешён для вашего домена)

### Проблема: Бот не обновляет сессию

- Проверить логи бота: `railway logs -s telegram-bot`
- Проверить, что API_URL правильный
- Проверить, что endpoint /api/update-session-telegram доступен

---

## Успешный деплой выглядит так:

```bash
✅ Миграция применена
✅ Backend задеплоен
✅ Frontend задеплоен
✅ Telegram Bot задеплоен
✅ Тестовая проверка прошла успешно
✅ UTM сохранились в БД
✅ session_id связался с check_request
```

---

## Контакты

Если что-то не работает — проверь логи:

```bash
# Backend logs
railway logs -s backend

# Telegram Bot logs
railway logs -s telegram-bot
```
