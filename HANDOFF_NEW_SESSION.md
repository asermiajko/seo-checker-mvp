# Handoff для новой сессии: SEO Checker MVP Deployment

## Текущее состояние проекта

### ✅ Что ВЫПОЛНЕНО (95% MVP):
- ✅ Backend (FastAPI + PostgreSQL) — готов, протестирован
- ✅ Telegram Bot — готов, протестирован
- ✅ Все тесты (unit, integration, e2e) — пройдены
- ✅ Документация — полная
- ✅ Проект перенесён в `/Users/aleksejsermazko/Documents/Cursor/work/git/projects/seo-checker-tool/`
- ✅ Git инициализирован, коммит создан локально
- ✅ Homebrew установлен, GitHub CLI установлен и авторизован
- ✅ Railway CLI установлен и авторизован (user: a.sermiajko@gmail.com)
- ✅ Railway проект создан: `seo-checker-backend` (ID: b21e4f50-40c2-435f-8bb1-c377355f889f)
- ✅ PostgreSQL добавлен в Railway
- ✅ Backend сервис создан в Railway (Service ID: 45de6a7c-9716-4efb-9e04-729494d1b027)

### ❌ Что НЕ ВЫПОЛНЕНО (осталось 5%):
- ❌ Код НЕ запушен в GitHub (репозиторий создан, но пуст)
- ❌ Backend НЕ задеплоен на Railway (сервис создан, но без кода)
- ❌ Telegram bot НЕ задеплоен на Railway
- ❌ Финальное тестирование в production

### 🔴 ПРОБЛЕМА в текущей сессии:
Shell tool сломан — все команды возвращают пустой output и выполняются за 0ms. Это сделало невозможным:
- Выполнение git push
- Деплой через Railway CLI
- Проверку статуса команд

## Следующие шаги (для новой сессии)

### Шаг 1: Git Push в GitHub
```bash
cd /Users/aleksejsermazko/Documents/Cursor/work/git/projects/seo-checker-tool

# Проверить статус
git status
git remote -v

# Если репозиторий на GitHub не существует
gh repo create seo-checker-mvp --public

# Добавить файлы и закоммитить
git add -A
git commit -m "feat: SEO Checker MVP - complete backend and telegram bot"

# Запушить
git push -u origin main
```

**Ожидаемый результат:** Код появится на https://github.com/asermiajko/seo-checker-mvp

### Шаг 2: Подключить GitHub к Railway (Backend)
1. Открыть: https://railway.com/project/b21e4f50-40c2-435f-8bb1-c377355f889f/service/45de6a7c-9716-4efb-9e04-729494d1b027
2. Settings → Source → Connect Repo
3. Выбрать репозиторий: `asermiajko/seo-checker-mvp`
4. **ВАЖНО:** Root Directory = `backend`
5. Railway автоматически запустит деплой

**Ожидаемый результат:** Backend задеплоится, появится публичный URL (через Settings → Networking → Generate Domain)

### Шаг 3: Проверить Backend
```bash
# Получить URL backend'а
curl https://<backend-url>/
curl https://<backend-url>/api/health
```

**Ожидаемый результат:**
```json
{"message":"SEO Checker API is running","version":"1.0.0"}
```

### Шаг 4: Деплой Telegram Bot
```bash
cd /Users/aleksejsermazko/Documents/Cursor/work/git/projects/seo-checker-tool/telegram-bot

# Инициализировать Railway для бота
railway init --name seo-checker-bot

# Установить переменные окружения
railway variables set TELEGRAM_TOKEN=8350120854:AAH9a6ugVBs7v6xd7tn7zYijkph5lIK4jAw
railway variables set API_URL=https://<backend-url>

# Деплой
railway up
```

**Ожидаемый результат:** Бот запустится и будет отвечать в Telegram

### Шаг 5: Тестирование в Production
1. Открыть Telegram, найти бота (по username из @BotFather)
2. Отправить `/start`
3. Отправить URL: `https://example.com`
4. Проверить, что бот возвращает отчёт

## Важные данные

### Telegram Bot Token
```
8350120854:AAH9a6ugVBs7v6xd7tn7zYijkph5lIK4jAw
```

### Railway Project IDs
- Project: `b21e4f50-40c2-435f-8bb1-c377355f889f`
- Backend Service: `45de6a7c-9716-4efb-9e04-729494d1b027`
- Project URL: https://railway.com/project/b21e4f50-40c2-435f-8bb1-c377355f889f

### Database
PostgreSQL уже создан в Railway, `DATABASE_URL` будет доступна автоматически для backend сервиса.

### Структура проекта
```
/Users/aleksejsermazko/Documents/Cursor/work/git/projects/seo-checker-tool/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── migrations/
│   ├── requirements.txt
│   ├── Procfile (release: alembic upgrade head + web: uvicorn)
│   ├── railway.json
│   └── start.sh
├── telegram-bot/
│   ├── bot.py
│   ├── handlers/
│   ├── services/
│   ├── requirements.txt
│   ├── Procfile (worker: python bot.py)
│   └── railway.json
├── specs/
├── README.md
└── DEPLOY.sh
```

## Конфигурация Backend

### Procfile
```
release: alembic upgrade head
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Миграции
- `backend/migrations/versions/4cffd1d19e60_initial_schema.py` — initial schema
- Миграция запустится автоматически при деплое через `release` command в Procfile

### Environment Variables (автоматические)
- `DATABASE_URL` — устанавливается Railway автоматически
- `ENVIRONMENT=production` — уже установлена
- `PORT` — устанавливается Railway автоматически

## Конфигурация Telegram Bot

### Procfile
```
worker: python bot.py
```

### Environment Variables (нужно установить)
- `TELEGRAM_TOKEN=8350120854:AAH9a6ugVBs7v6xd7tn7zYijkph5lIK4jAw`
- `API_URL=https://<backend-url>` (установить после деплоя backend)

## Альтернативный способ (если Railway CLI не работает)

### Backend через GitHub UI:
1. Создать репо на GitHub: https://github.com/new (name: `seo-checker-mvp`)
2. Локально: `git push -u origin main`
3. Railway: Settings → Source → Connect Repo → выбрать `seo-checker-mvp` → Root Directory: `backend`

### Bot через Railway UI:
1. Railway → New Service → Empty Service
2. Settings → Source → Connect Repo → выбрать `seo-checker-mvp` → Root Directory: `telegram-bot`
3. Variables → добавить `TELEGRAM_TOKEN` и `API_URL`

## Проблемы, которые могут возникнуть

### 1. Database connection error
**Симптом:** Backend не стартует, ошибка "could not connect to database"
**Решение:** Проверить, что `DATABASE_URL` в переменных окружения содержит `postgresql+asyncpg://` (не `postgresql://`)

### 2. Миграции не применились
**Симптом:** 500 ошибка при обращении к API
**Решение:** Запустить вручную: `railway run alembic upgrade head` (из папки `backend`)

### 3. Бот не отвечает
**Симптом:** Telegram бот не реагирует на сообщения
**Решение:** Проверить логи: `railway logs` (из папки `telegram-bot`)

### 4. 502 Bad Gateway
**Симптом:** Backend URL возвращает 502
**Решение:** Проверить логи деплоя в Railway UI, убедиться что `Procfile` корректен

## Финальная проверка (чеклист)

- [ ] Код в GitHub: https://github.com/asermiajko/seo-checker-mvp
- [ ] Backend работает: `curl <backend-url>/` → 200 OK
- [ ] Health check: `curl <backend-url>/api/health` → `{"status":"ok"}`
- [ ] Database работает: health check показывает `"database":"ok"`
- [ ] Бот отвечает в Telegram на `/start`
- [ ] Бот проверяет сайт и возвращает отчёт
- [ ] Deep link работает: `/start check_<base64_url>`

## Контакты и ссылки

- GitHub (будет): https://github.com/asermiajko/seo-checker-mvp
- Railway: https://railway.com/project/b21e4f50-40c2-435f-8bb1-c377355f889f
- Railway Account: a.sermiajko@gmail.com

## Время на выполнение оставшихся шагов
- Шаг 1 (Git Push): 2 минуты
- Шаг 2 (Backend Deploy): 3-5 минут (ожидание деплоя)
- Шаг 3 (Проверка Backend): 1 минута
- Шаг 4 (Bot Deploy): 3-5 минут
- Шаг 5 (Тестирование): 2 минуты

**Итого: 10-15 минут до полного запуска MVP** 🚀
