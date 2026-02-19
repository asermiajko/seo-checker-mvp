# UTM Tracking & Session Attribution — Implementation Summary

## Дата: 2026-02-19

## Обзор изменений

Реализован полный цикл атрибуции пользователей с веб-формы до проверки в Telegram-боте с сохранением UTM-меток для аналитики эффективности каналов.

---

## Архитектура решения

### Флоу пользователя:

1. **Веб-форма (Landing Page)**
   - Пользователь попадает на страницу с UTM-метками (например: `?utm_source=google&utm_campaign=seo_check`)
   - Кликает "Открыть Telegram-бот"
   - Генерируется уникальный `session_id` (UUID)
   - UTM-метки + `session_id` отправляются на backend (`POST /api/track-session`)
   - Открывается Telegram с deep link: `https://t.me/bot?start=session_{UUID}`

2. **Telegram Bot (Start)**
   - Пользователь переходит в бота по deep link
   - Бот получает `session_id` из параметра `/start session_UUID`
   - Обновляет сессию в БД: добавляет `telegram_id` + `telegram_username` + `bot_started_at`
   - Показывает приветствие: "Отправьте URL сайта для проверки"

3. **Telegram Bot (Проверка)**
   - Пользователь отправляет URL (например: `https://example.com`)
   - Бот вызывает API `/api/check` с `telegram_id` + `site_url` + `session_id`
   - Backend создаёт `CheckRequest` со связью `session_id → WebSession`
   - Отправляет результат проверки

4. **Аналитика**
   - В БД есть полная цепочка: UTM-метки → Telegram-пользователь → Проверки
   - Можно строить воронку конверсии по каналам

---

## База данных

### Новая таблица: `web_sessions`

```sql
CREATE TABLE web_sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    
    -- UTM tracking
    utm_source VARCHAR(255),
    utm_medium VARCHAR(255),
    utm_campaign VARCHAR(255),
    utm_term VARCHAR(255),
    utm_content VARCHAR(255),
    referrer TEXT,
    user_agent TEXT,
    
    -- Telegram data (filled when user opens bot)
    telegram_id BIGINT,
    telegram_username VARCHAR(255),
    bot_started_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_web_sessions_session_id ON web_sessions(session_id);
CREATE INDEX ix_web_sessions_telegram_id ON web_sessions(telegram_id);
```

### Изменения в `check_requests`

```sql
ALTER TABLE check_requests 
ADD COLUMN session_id UUID,
ADD CONSTRAINT fk_check_requests_session_id 
    FOREIGN KEY (session_id) 
    REFERENCES web_sessions(session_id) 
    ON DELETE SET NULL;

CREATE INDEX ix_check_requests_session_id ON check_requests(session_id);
```

---

## Backend изменения

### 1. Models (`app/models.py`)
- Добавлена модель `WebSession`
- Добавлена связь `CheckRequest.session_id → WebSession.session_id`

### 2. Schemas (`app/schemas.py`)
- `TrackSessionRequestSchema` — для сохранения UTM-меток
- `UpdateSessionTelegramSchema` — для обновления сессии с Telegram-данными
- `SessionResponseSchema` — ответ для session endpoints
- `CheckRequestSchema` — добавлено поле `session_id: Optional[UUID]`

### 3. Routes (`app/routes/session.py` — новый файл)
- `POST /api/track-session` — создание сессии с UTM-метками
- `POST /api/update-session-telegram` — обновление сессии с Telegram ID/username

### 4. Routes (`app/routes/check.py`)
- Добавлена передача `session_id` в `CheckRequest` (опциональная)

### 5. Main (`app/main.py`)
- Подключен `session_router`

---

## Frontend изменения

### 1. HTML (`frontend/index.html`)
- **Удалена** форма с инпутом для ввода URL
- **Добавлена** CTA-кнопка "Открыть Telegram-бот" (`id="openTelegramButton"`)
- Обновлён текст: призыв отправить URL уже в боте

### 2. JavaScript (`frontend/script.js`)
- **Удалена** логика сабмита формы с энкодингом URL
- **Добавлена** логика:
  - Генерация `session_id` через `crypto.randomUUID()`
  - Извлечение UTM-меток из URL: `new URLSearchParams(window.location.search)`
  - POST на `/api/track-session` с UTM + `session_id`
  - Открытие Telegram с deep link: `https://t.me/bot?start=session_{UUID}`

---

## Telegram Bot изменения

### 1. Start handler (`telegram-bot/handlers/start.py`)
- **Удалена** логика обработки `check_BASE64_URL` (старый deep link)
- **Добавлена** логика обработки `session_UUID`:
  - Парсинг UUID из `/start session_UUID`
  - POST на `/api/update-session-telegram` для обновления сессии
  - Сохранение `session_id` в `context.user_data` для последующих проверок
- **Обновлено** приветствие: убран призыв идти на веб-форму

### 2. URL handler (`telegram-bot/handlers/url.py`)
- **Добавлена** передача `session_id` из `context.user_data` в API
- **Удалено** упоминание веб-формы в сообщениях об ошибках

### 3. API Client (`telegram-bot/services/api_client.py`)
- Метод `check_site()` теперь принимает `session_id: Optional[str]`
- Передаёт `session_id` в payload, если он есть

---

## Миграция базы данных

### Файл миграции: `backend/migrations/versions/add_web_sessions_table.py`

**Revision ID**: `a1b2c3d4e5f6`  
**Revises**: `4cffd1d19e60`

### Применение миграции:

```bash
cd backend/
alembic upgrade head
```

**Важно**: Миграция должна быть применена **до** деплоя нового кода!

---

## Деплой

### Последовательность:

1. **Backend**
   ```bash
   # Применить миграцию на production БД
   railway run alembic upgrade head
   
   # Задеплоить новый код
   git push origin main
   railway up
   ```

2. **Frontend**
   ```bash
   # Задеплоить новый frontend (Vercel/GitHub Pages)
   git push origin main
   vercel --prod
   ```

3. **Telegram Bot**
   ```bash
   # Задеплоить новый код бота
   git push origin main
   railway up
   ```

---

## Тестирование

### 1. Проверка флоу с UTM-метками:

```bash
# Открыть в браузере:
https://your-landing.com/?utm_source=test&utm_medium=manual&utm_campaign=testing

# Нажать "Открыть Telegram-бот"
# → Проверить в консоли браузера: успешный POST на /api/track-session
# → Открывается Telegram с deep link

# В Telegram:
# → Отправить /start (или автоматически при переходе)
# → Отправить URL: https://example.com
# → Получить отчёт

# Проверить БД:
SELECT 
  ws.session_id,
  ws.utm_source,
  ws.utm_campaign,
  ws.telegram_id,
  ws.bot_started_at,
  cr.site_url,
  cr.created_at
FROM web_sessions ws
LEFT JOIN check_requests cr ON ws.session_id = cr.session_id
WHERE ws.telegram_id = YOUR_TELEGRAM_ID;
```

### 2. Проверка прямого захода в бота (без веб-формы):

```bash
# Открыть бота напрямую: https://t.me/site_SEO_cheker_bot
# → Нажать /start
# → Отправить URL: https://example.com
# → Получить отчёт

# В БД:
# → check_requests.session_id должен быть NULL (нормально)
```

---

## Аналитика: SQL-запросы

### Конверсия по источникам

```sql
SELECT 
  utm_source,
  utm_campaign,
  COUNT(*) as visits,
  COUNT(telegram_id) as bot_opens,
  COUNT(DISTINCT cr.id) as checks_made,
  ROUND(COUNT(DISTINCT cr.id)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as conversion_rate
FROM web_sessions ws
LEFT JOIN check_requests cr ON ws.session_id = cr.session_id
WHERE ws.created_at > NOW() - INTERVAL '30 days'
GROUP BY utm_source, utm_campaign
ORDER BY checks_made DESC;
```

### Воронка по дням

```sql
SELECT 
  DATE(ws.created_at) as date,
  COUNT(*) as web_visits,
  COUNT(ws.telegram_id) as bot_opens,
  COUNT(DISTINCT cr.id) as checks_made
FROM web_sessions ws
LEFT JOIN check_requests cr ON ws.session_id = cr.session_id
WHERE ws.created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(ws.created_at)
ORDER BY date DESC;
```

### Топ UTM-кампаний по конверсии

```sql
SELECT 
  utm_campaign,
  COUNT(*) as total_sessions,
  COUNT(DISTINCT cr.id) as checks,
  ROUND(COUNT(DISTINCT cr.id)::numeric / COUNT(*) * 100, 2) as cvr
FROM web_sessions ws
LEFT JOIN check_requests cr ON ws.session_id = cr.session_id
WHERE utm_campaign IS NOT NULL
GROUP BY utm_campaign
HAVING COUNT(*) > 5
ORDER BY cvr DESC;
```

---

## Обратная совместимость

- ✅ Пользователи, которые открывают бота напрямую (без веб-формы), работают как раньше
- ✅ Старые записи `check_requests` без `session_id` остаются валидными (NULL допустим)
- ✅ Веб-форма больше не требует ввода URL → проще UX

---

## Дальнейшие улучшения

1. **Dashboard для аналитики**
   - Metabase / Redash для визуализации конверсий
   - Еженедельные email-отчёты по каналам

2. **Retargeting**
   - Если пользователь открыл бота, но не сделал проверку → отправить напоминание через 24 часа

3. **A/B тестирование**
   - Разные варианты CTA на веб-форме
   - Tracking в `utm_content`

4. **Расширенная атрибуция**
   - Привязка нескольких проверок к одному пользователю (по `telegram_id`)
   - LTV (Lifetime Value) по каналам

---

## Контакты

**Автор**: Claude (Cursor Agent)  
**Дата**: 2026-02-19  
**Проект**: SEO Checker MVP
