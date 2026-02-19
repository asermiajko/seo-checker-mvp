# Telegram Bot Integration — SEO Checker

## Архитектура флоу

### Пользовательский флоу:
1. Пользователь вводит URL сайта на веб-странице
2. Нажимает "Получить отчёт в Telegram"
3. Открывается Telegram с deep link: `https://t.me/your_bot?start=check_ENCODED_URL`
4. Пользователь нажимает START или пишет /start
5. Бот получает команду, парсит URL, запускает проверку
6. Бот отправляет отчёт пользователю
7. Бот сохраняет в БД: `telegram_id`, `username`, `site_url`, `timestamp`

---

## 1. Создание Telegram-бота

### Шаг 1: Регистрация бота
1. Открой Telegram, найди @BotFather
2. Отправь `/newbot`
3. Придумай имя: `SEO Checker for Developers`
4. Придумай username: `seo_checker_bot` (или другой доступный)
5. Получи **API Token** (сохрани его)

### Шаг 2: Обновить username в коде
В `script.js`:
```javascript
const TELEGRAM_BOT_USERNAME = 'seo_checker_bot'; // Замени на свой
```

---

## 2. Telegram Bot Handler (Python)

### Структура проекта:
```
telegram-bot/
├── bot.py              # Главный файл бота
├── seo_checker.py      # Логика SEO-проверок
├── database.py         # Работа с БД
├── config.py           # Конфигурация
├── requirements.txt    # Зависимости
└── .env                # Секреты (токены)
```

### `requirements.txt`:
```
python-telegram-bot==20.7
aiohttp==3.9.1
beautifulsoup4==4.12.2
lxml==5.1.0
playwright==1.40.0
openai==1.6.1
python-dotenv==1.0.0
psycopg2-binary==2.9.9  # или sqlite3 для простоты
```

### `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:password@localhost/seo_checker
```

---

## 3. Основной код бота (`bot.py`)

```python
import os
import logging
from urllib.parse import unquote
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

from seo_checker import run_seo_check
from database import save_check_request, save_check_result

# Загрузить переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ==========================================
# Handler: /start с deep link
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    Формат deep link: /start check_ENCODED_URL
    """
    user = update.effective_user
    telegram_id = user.id
    username = user.username or user.first_name
    
    # Получить аргументы из deep link
    args = context.args
    
    if not args:
        # Обычный /start без параметров
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            "Я проверяю SEO сайтов застройщиков.\n\n"
            "Чтобы получить отчёт:\n"
            "1. Перейди на сайт проверки\n"
            "2. Введи URL своего сайта\n"
            "3. Нажми кнопку — я пришлю отчёт сюда"
        )
        return
    
    # Парсинг URL из deep link
    deep_link_param = args[0]
    
    if not deep_link_param.startswith('check_'):
        await update.message.reply_text(
            "❌ Неверная ссылка. Пожалуйста, используйте форму на сайте."
        )
        return
    
    # Извлечь URL
    encoded_url = deep_link_param.replace('check_', '')
    site_url = unquote(encoded_url)
    
    # Сохранить запрос в БД
    check_id = await save_check_request(telegram_id, username, site_url)
    
    # Отправить сообщение о начале проверки
    await update.message.reply_text(
        f"🔍 Запускаю проверку сайта:\n{site_url}\n\n"
        "⏳ Это займёт 30-60 секунд..."
    )
    
    # Запустить проверку асинхронно
    try:
        report = await run_seo_check(site_url)
        
        # Сохранить результат в БД
        await save_check_result(check_id, report)
        
        # Отправить отчёт
        await send_report(update, report)
        
    except Exception as e:
        logger.error(f"Error checking site {site_url}: {e}")
        await update.message.reply_text(
            f"❌ Не удалось проверить сайт.\n\n"
            f"Возможные причины:\n"
            f"• Сайт недоступен\n"
            f"• Превышено время ожидания\n"
            f"• Ошибка сервера\n\n"
            f"Попробуйте ещё раз через несколько минут."
        )

# ==========================================
# Отправка отчёта
# ==========================================

async def send_report(update: Update, report: dict):
    """
    Отправить отчёт пользователю
    """
    # Формируем текст отчёта
    score = report['score']
    problems_critical = report['problems_critical']
    problems_important = report['problems_important']
    checks_ok = report['checks_ok']
    
    # Эмодзи для скора
    if score >= 8:
        score_emoji = "🟢"
    elif score >= 5:
        score_emoji = "🟡"
    else:
        score_emoji = "🔴"
    
    message = f"""
🎯 <b>SEO-скор вашего сайта: {score}/10</b> {score_emoji}

{score_emoji if problems_critical > 0 else "✅"} Критичные проблемы: {problems_critical}
{"🟡" if problems_important > 0 else "✅"} Важные доработки: {problems_important}
✅ Всё хорошо: {checks_ok}

━━━━━━━━━━━━━━━━━━━━━

📊 <b>Результаты по категориям:</b>

{format_categories(report['categories'])}

━━━━━━━━━━━━━━━━━━━━━

🚨 <b>Что исправить в первую очередь:</b>

{format_top_priorities(report['top_priorities'])}

━━━━━━━━━━━━━━━━━━━━━

💡 <b>Хорошая новость!</b>

Все эти проблемы решаются за 1 час в конструкторе Ida.Lite.

👉 <a href="https://idalite.ru">Попробовать Ida.Lite бесплатно</a>
👉 <a href="https://idalite.ru/demo">Записаться на демо</a>
"""
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        disable_web_page_preview=True
    )

def format_categories(categories: list) -> str:
    """Форматировать категории для отчёта"""
    result = []
    for cat in categories:
        emoji = "✅" if cat['score'] == cat['total'] else "⚠️" if cat['score'] > 0 else "❌"
        result.append(f"{emoji} {cat['name']}: {cat['score']}/{cat['total']}")
    return "\n".join(result)

def format_top_priorities(priorities: list) -> str:
    """Форматировать топ-3 приоритета"""
    result = []
    for i, priority in enumerate(priorities[:3], 1):
        result.append(f"{i}. {priority['severity']} {priority['title']}\n   → {priority['action']}")
    return "\n\n".join(result)

# ==========================================
# Handler: /help
# ==========================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    await update.message.reply_text(
        "📖 <b>Как пользоваться ботом:</b>\n\n"
        "1. Перейдите на сайт проверки SEO\n"
        "2. Введите URL вашего сайта\n"
        "3. Нажмите кнопку — отчёт придёт в этот чат\n\n"
        "Бот проверяет 13 важных SEO-параметров:\n"
        "• Техническую базу (robots.txt, sitemap, скорость)\n"
        "• Структуру контента (title, H1, фильтры)\n"
        "• Микроразметку (Schema.org, OpenGraph)\n"
        "• И многое другое\n\n"
        "Время проверки: 30-60 секунд",
        parse_mode='HTML'
    )

# ==========================================
# Main
# ==========================================

def main():
    """Запуск бота"""
    # Создать приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавить handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Запустить бота
    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
```

---

## 4. База данных (`database.py`)

```python
import asyncio
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# ==========================================
# Database Schema
# ==========================================

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS check_requests (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    username VARCHAR(255),
    site_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS check_results (
    id SERIAL PRIMARY KEY,
    check_request_id INTEGER REFERENCES check_requests(id),
    score DECIMAL(3, 1),
    problems_critical INTEGER,
    problems_important INTEGER,
    checks_ok INTEGER,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_telegram_id ON check_requests(telegram_id);
CREATE INDEX idx_site_url ON check_requests(site_url);
CREATE INDEX idx_created_at ON check_requests(created_at);
"""

# ==========================================
# Database Functions
# ==========================================

async def init_db():
    """Инициализация БД"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(CREATE_TABLES)
    conn.commit()
    cur.close()
    conn.close()

async def save_check_request(telegram_id: int, username: str, site_url: str) -> int:
    """Сохранить запрос на проверку"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO check_requests (telegram_id, username, site_url) VALUES (%s, %s, %s) RETURNING id",
        (telegram_id, username, site_url)
    )
    
    check_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return check_id

async def save_check_result(check_request_id: int, report: dict):
    """Сохранить результат проверки"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute(
        """
        INSERT INTO check_results 
        (check_request_id, score, problems_critical, problems_important, checks_ok, report_data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            check_request_id,
            report['score'],
            report['problems_critical'],
            report['problems_important'],
            report['checks_ok'],
            report  # Сохранить весь отчёт как JSONB
        )
    )
    
    conn.commit()
    cur.close()
    conn.close()
```

---

## 5. Логика SEO-проверок (`seo_checker.py`)

```python
import asyncio
from typing import Dict, List

# Импортируйте ваши функции проверки из спецификации
# from checks.robots import check_robots
# from checks.sitemap import check_sitemap
# и т.д.

async def run_seo_check(site_url: str) -> Dict:
    """
    Запустить все SEO-проверки
    Возвращает отчёт в формате для отправки пользователю
    """
    
    # Запустить все проверки асинхронно
    results = await asyncio.gather(
        check_robots(site_url),
        check_sitemap(site_url),
        check_speed(site_url),
        check_html_sitemap(site_url),
        check_noindex(site_url),
        check_title_description(site_url),
        check_headings(site_url),
        check_filter_pages(site_url),
        check_schema(site_url),
        check_opengraph(site_url),
        check_canonical(site_url),
        check_local_seo(site_url),
        check_analytics(site_url),
        return_exceptions=True
    )
    
    # Собрать результаты
    report = compile_report(results)
    
    return report

def compile_report(results: List) -> Dict:
    """
    Скомпилировать финальный отчёт
    """
    # Подсчитать статистику
    total_checks = 13
    checks_ok = sum(1 for r in results if r.get('status') == 'ok')
    checks_partial = sum(1 for r in results if r.get('status') == 'partial')
    checks_problem = sum(1 for r in results if r.get('status') == 'problem')
    
    # Подсчитать скор
    score = (checks_ok * 1.0 + checks_partial * 0.5) / total_checks * 10
    
    # Определить топ-3 приоритета
    top_priorities = get_top_priorities(results)
    
    return {
        'score': round(score, 1),
        'problems_critical': checks_problem,
        'problems_important': checks_partial,
        'checks_ok': checks_ok,
        'categories': group_by_categories(results),
        'top_priorities': top_priorities,
        'detailed_results': results
    }
```

---

## 6. Deployment

### Вариант 1: VPS (Railway, DigitalOcean, Heroku)
```bash
# Установить зависимости
pip install -r requirements.txt

# Установить Playwright browsers
playwright install chromium

# Запустить бота
python bot.py
```

### Вариант 2: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

CMD ["python", "bot.py"]
```

---

## 7. Тестирование

### Локальное тестирование:
1. Создай `.env` с токеном
2. Запусти `python bot.py`
3. Открой веб-форму в браузере
4. Введи URL и нажми кнопку
5. Проверь, что Telegram открылся
6. Нажми START в боте
7. Получи отчёт

---

## 8. Аналитика и мониторинг

### Метрики для отслеживания:
- Количество проверок в день
- Популярные домены (сколько раз проверяли)
- Средний скор сайтов
- Топ-3 проблемы (какие чаще всего встречаются)
- Конверсия: форма → Telegram → отчёт получен

### SQL-запросы для аналитики:
```sql
-- Статистика за сегодня
SELECT 
    COUNT(*) as total_checks,
    COUNT(DISTINCT telegram_id) as unique_users,
    AVG(score) as avg_score
FROM check_requests cr
LEFT JOIN check_results cres ON cr.id = cres.check_request_id
WHERE DATE(cr.created_at) = CURRENT_DATE;

-- Топ-10 доменов
SELECT 
    SUBSTRING(site_url FROM 'https?://([^/]+)') as domain,
    COUNT(*) as check_count
FROM check_requests
GROUP BY domain
ORDER BY check_count DESC
LIMIT 10;
```

---

## Что дальше?

1. ✅ Веб-форма готова
2. ⏭️ Создать Telegram-бота (@BotFather)
3. ⏭️ Реализовать `bot.py` (handlers)
4. ⏭️ Реализовать `seo_checker.py` (логика проверок из спецификации v2)
5. ⏭️ Настроить БД (PostgreSQL или SQLite)
6. ⏭️ Деплой на сервер
7. ⏭️ Тестирование
8. ⏭️ Добавить в статью ссылку на форму
