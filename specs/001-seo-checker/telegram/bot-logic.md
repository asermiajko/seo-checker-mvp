# Telegram Bot Logic

**Module**: Telegram  
**Library**: python-telegram-bot 20.7  
**Last Updated**: 2026-02-18

---

## Overview

The Telegram bot acts as a **thin client**:
- Receives deep link from web form
- Extracts site URL
- Calls Backend API
- Formats and sends report to user

**No SEO logic in the bot** — all checks are delegated to Backend API.

---

## Bot Commands

### 1. /start

**Without arguments** (user clicks "Start" in bot):
```
/start
```

**Response**:
```
👋 Привет! Я проверяю SEO сайтов застройщиков.

Чтобы проверить сайт:
1. Перейдите на https://checker.idalite.ru
2. Введите URL сайта
3. Вернитесь сюда за результатом

Или отправьте мне URL прямо сейчас.
```

---

**With deep link** (user opens from web form):
```
/start check_aHR0cHM6Ly9leGFtcGxlLnJ1
```

**Flow**:
1. Parse `check_` parameter
2. Decode Base64 → `https://example.ru`
3. Send "⏳ Проверяю сайт..." message
4. Call API: `POST /api/check`
5. Wait for response (timeout: 150 sec)
6. Format report
7. Send to user

---

### 2. /help

**Command**:
```
/help
```

**Response**:
```
ℹ️ Как пользоваться:

1️⃣ Откройте форму: https://checker.idalite.ru
2️⃣ Введите URL сайта
3️⃣ Получите отчёт здесь

Я проверяю:
✅ Robots.txt и Sitemap
✅ Title и Description
✅ Структуру заголовков
✅ Счётчики аналитики
✅ И ещё 4 параметра

Проверка занимает ~30 секунд.
```

---

### 3. /history (v1.1)

**Command**:
```
/history
```

**Response**:
```
📊 Ваши проверки:

1. example.ru — 7.5/10 (18 фев, 15:30)
2. test.ru — 5.0/10 (17 фев, 10:00)
3. demo.ru — 8.5/10 (16 фев, 14:20)

Всего проверок: 15
```

---

## Deep Link Format

**Web form generates**:
```
https://t.me/seo_checker_bot?start=check_ENCODED_URL
```

**Example**:
```
Site URL: https://example.ru
Encoded: aHR0cHM6Ly9leGFtcGxlLnJ1
Deep link: https://t.me/seo_checker_bot?start=check_aHR0cHM6Ly9leGFtcGxlLnJ1
```

**Bot receives**:
```python
def handle_start(update, context):
    args = context.args  # ["check_aHR0cHM6Ly9leGFtcGxlLnJ1"]
    if args and args[0].startswith("check_"):
        encoded = args[0].replace("check_", "")
        site_url = base64.b64decode(encoded).decode()
        # Process check...
```

---

## Message Flow

### Step 1: Initial Message

**User opens bot with deep link**

Bot sends immediately:
```
⏳ Проверяю сайт example.ru...

Это займёт ~30 секунд.
```

### Step 2: API Call

```python
async def run_check(site_url, telegram_id):
    api_url = os.getenv("API_URL")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_url}/api/check",
            json={"site_url": site_url, "telegram_id": telegram_id},
            timeout=150.0
        )
        return response.json()
```

### Step 3: Report Message

**If successful**:
```
🟢 SEO-скор: 7.5/10

━━━━━━━━━━━━━━━━

📊 Результаты:
❌ Критичные проблемы: 1
⚠️ Важные: 1
✅ Всё хорошо: 6

━━━━━━━━━━━━━━━━

📂 По категориям:
⚙️ Техническая база: 4/5
📝 Контент: 2/2
🏗 Структура: 1/1

━━━━━━━━━━━━━━━━

🚨 Топ проблемы:

1. ❌ Главная страница закрыта от индексации
   → Удалите тег <meta name='robots' content='noindex'>

2. ⚠️ Title слишком короткий (15 символов)
   → Рекомендуется 30-65 символов

━━━━━━━━━━━━━━━━

💡 Эти проблемы решаются в Ida.Lite!
🚀 Мы автоматизируем SEO для застройщиков.

👉 [Узнать больше](https://idalite.ru)
```

**If error (timeout)**:
```
⚠️ Проверка заняла слишком много времени.

Возможные причины:
• Сайт медленно отвечает
• Много страниц на проверку
• Временные проблемы с сервером

Попробуйте ещё раз через несколько минут.
```

**If error (rate limit)**:
```
⚠️ Вы превысили лимит проверок (5 в час).

Попробуйте через 23 минуты.

💡 Если вам нужно больше проверок, свяжитесь с нами: @ida_lite_support
```

---

## Report Formatting

### Formatter Function

```python
def format_report(report: dict) -> str:
    """Convert API response to Telegram Markdown."""
    score = report["score"]
    
    # Emoji based on score
    if score >= 8:
        emoji = "🟢"
        level = "Отлично"
    elif score >= 6:
        emoji = "🟡"
        level = "Хорошо"
    elif score >= 4:
        emoji = "🟠"
        level = "Требуется улучшение"
    else:
        emoji = "🔴"
        level = "Критично"
    
    # Header
    text = f"{emoji} **SEO-скор: {score}/10** ({level})\n\n"
    text += "━━━━━━━━━━━━━━━━\n\n"
    
    # Summary
    text += "📊 **Результаты:**\n"
    text += f"❌ Критичные проблемы: {report['problems_critical']}\n"
    text += f"⚠️ Важные: {report['problems_important']}\n"
    text += f"✅ Всё хорошо: {report['checks_ok']}\n\n"
    text += "━━━━━━━━━━━━━━━━\n\n"
    
    # Categories
    text += "📂 **По категориям:**\n"
    for cat in report["categories"]:
        text += f"{get_category_emoji(cat['name'])} {cat['name']}: {cat['score']}/{cat['total']}\n"
    text += "\n━━━━━━━━━━━━━━━━\n\n"
    
    # Top Priorities
    if report["top_priorities"]:
        text += "🚨 **Топ проблемы:**\n\n"
        for i, priority in enumerate(report["top_priorities"][:3], 1):
            severity_emoji = "❌" if priority["severity"] == "critical" else "⚠️"
            text += f"{i}. {severity_emoji} {priority['title']}\n"
            text += f"   → {priority['action']}\n\n"
        text += "━━━━━━━━━━━━━━━━\n\n"
    
    # CTA (personalized based on score)
    if score < 5:
        text += "💡 **Ваш сайт нуждается в серьёзной оптимизации!**\n"
        text += "Ida.Lite автоматизирует SEO для застройщиков.\n\n"
        text += "🚀 [Попробовать бесплатно](https://idalite.ru)\n"
    elif score < 8:
        text += "💡 Эти проблемы решаются в Ida.Lite!\n\n"
        text += "👉 [Узнать больше](https://idalite.ru)\n"
    else:
        text += "✅ Ваш сайт в отличном состоянии!\n\n"
        text += "💡 Хотите держать SEO на автопилоте? [Попробуйте Ida.Lite](https://idalite.ru)\n"
    
    return text


def get_category_emoji(category_name: str) -> str:
    """Get emoji for category."""
    emojis = {
        "Техническая база": "⚙️",
        "Контент": "📝",
        "Структура": "🏗",
        "SEO улучшения": "🔍",
        "Социальные сети": "📱"
    }
    return emojis.get(category_name, "📊")
```

---

## Error Handling

### API Errors

```python
async def call_api(site_url, telegram_id):
    try:
        response = await client.post(api_url, json={...}, timeout=150.0)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            error = response.json()["error"]
            return {"error": "rate_limit", "message": error["message"]}
        elif response.status_code == 400:
            return {"error": "validation", "message": "Некорректный URL"}
        else:
            return {"error": "server", "message": "Ошибка сервера"}
    
    except httpx.TimeoutException:
        return {"error": "timeout", "message": "Проверка заняла слишком много времени"}
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"error": "unknown", "message": "Неизвестная ошибка"}
```

### User Messages

```python
def handle_error(error_type, message):
    if error_type == "rate_limit":
        return f"⚠️ {message}"
    elif error_type == "timeout":
        return "⚠️ Проверка заняла слишком много времени. Попробуйте позже."
    elif error_type == "validation":
        return "❌ Некорректный URL. Проверьте адрес сайта."
    else:
        return "⚠️ Произошла ошибка. Попробуйте позже или свяжитесь с поддержкой."
```

---

## Bot Structure (Files)

```
telegram-bot/
├── bot.py                  # Main entry point
├── handlers/
│   ├── start.py           # /start handler
│   ├── help.py            # /help handler
│   └── history.py         # /history handler (v1.1)
├── services/
│   ├── api_client.py      # Backend API client
│   └── formatter.py       # Report formatting
├── utils/
│   ├── logger.py          # Logging setup
│   └── validators.py      # URL validation
├── requirements.txt
└── .env.example
```

---

## Environment Variables

```bash
# .env
BOT_TOKEN=123456:ABC-DEF...
API_URL=https://api.seo-checker.idalite.ru
LOG_LEVEL=INFO
```

---

## Deployment (Railway)

```yaml
# railway.json (or railway.toml)
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Start Command**:
```bash
python bot.py
```

**Bot runs in webhook mode** (not polling) in production:
```python
# bot.py
if __name__ == "__main__":
    if os.getenv("ENVIRONMENT") == "production":
        # Webhook mode
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8443)),
            webhook_url=f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}/webhook"
        )
    else:
        # Polling mode (local dev)
        app.run_polling()
```

---

## Testing

### Unit Tests

```python
# tests/test_formatter.py
def test_format_report_high_score():
    report = {
        "score": 8.5,
        "problems_critical": 0,
        "problems_important": 1,
        "checks_ok": 7,
        "categories": [...],
        "top_priorities": [...]
    }
    
    text = format_report(report)
    
    assert "🟢" in text
    assert "8.5/10" in text
    assert "Отлично" in text
```

### Integration Tests

```python
# tests/test_api_client.py
@pytest.mark.asyncio
async def test_call_api_success():
    client = APIClient(api_url="https://api.test.ru")
    
    with aioresponses() as m:
        m.post("https://api.test.ru/api/check", payload={"score": 7.5})
        
        result = await client.check_site("https://example.ru", 123456789)
        
        assert result["score"] == 7.5
```

---

## Next Steps

1. Review bot logic
2. Implement handlers
3. Write tests
4. Deploy to Railway

---

**Related Documents**:
- [API Contracts](../api/contracts.md)
- [Architecture Overview](../architecture/overview.md)
- [Data Flow](../architecture/data-flow.md)
