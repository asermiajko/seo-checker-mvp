# Quick Migration Guide

## Перед деплоем — ОБЯЗАТЕЛЬНО!

### 1. Проверить, что бэкенд работает:

```bash
# Локально
cd backend/
uvicorn app.main:app --reload

# На Railway
railway status
```

### 2. Применить миграцию на production:

```bash
cd backend/

# Вариант 1: Railway CLI (если alembic в PATH)
railway run alembic upgrade head

# Вариант 2: Python module (если alembic не в PATH)
railway run python -m alembic upgrade head

# Проверить результат:
railway run psql -c "\dt web_sessions"
# Должна появиться таблица web_sessions
```

### 3. Проверить структуру:

```bash
railway run psql -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'web_sessions'
ORDER BY ordinal_position;
"
```

**Ожидаемый результат:**
```
     column_name     |          data_type
---------------------+-----------------------------
 id                  | integer
 session_id          | uuid
 utm_source          | character varying
 utm_medium          | character varying
 utm_campaign        | character varying
 utm_term            | character varying
 utm_content         | character varying
 referrer            | text
 user_agent          | text
 telegram_id         | bigint
 telegram_username   | character varying
 bot_started_at      | timestamp without time zone
 created_at          | timestamp without time zone
 updated_at          | timestamp without time zone
```

### 4. Проверить связь с check_requests:

```bash
railway run psql -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'check_requests' AND column_name = 'session_id';
"
```

**Ожидаемый результат:**
```
 column_name | data_type
-------------+-----------
 session_id  | uuid
```

---

## После миграции

### 5. Задеплоить код:

```bash
git add .
git commit -m "feat: add UTM tracking and session attribution"
git push origin main

# Railway автоматически задеплоит backend + bot
```

### 6. Проверить работу:

1. **Открыть landing** (frontend)
2. **Кликнуть кнопку** "Открыть Telegram-бот"
3. **В Telegram** отправить URL: `https://example.com`
4. **Проверить БД**:

```bash
railway run psql -c "
SELECT 
  ws.session_id,
  ws.utm_source,
  ws.telegram_id,
  cr.site_url
FROM web_sessions ws
LEFT JOIN check_requests cr ON ws.session_id = cr.session_id
ORDER BY ws.created_at DESC
LIMIT 5;
"
```

---

## Rollback (если что-то не так)

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

## Проблемы и решения

### Проблема: "alembic: command not found"

**Решение:**
```bash
railway run python -m alembic upgrade head
```

### Проблема: "relation web_sessions already exists"

**Решение:** Миграция уже применена. Проверить:
```bash
railway run alembic current
# Должно показать: a1b2c3d4e5f6 (head)
```

### Проблема: "column session_id of relation check_requests already exists"

**Решение:** Миграция уже применена частично. Откатить и применить заново:
```bash
railway run alembic downgrade 4cffd1d19e60
railway run alembic upgrade head
```

---

## Готово! ✅

После успешной миграции:
- ✅ Таблица `web_sessions` создана
- ✅ Колонка `session_id` добавлена в `check_requests`
- ✅ Foreign key установлен
- ✅ Индексы созданы

Можно деплоить код!
