"""URL message handler for SEO Checker bot."""

import logging
import re
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIClient
import os

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")
api_client = APIClient(api_url=API_URL)


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL sent by user.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Validate URL format (simplified to support punycode/cyrillic domains)
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'  # subdomains
        r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'  # domain
        r'(?:\.[a-zA-Z]{2,})?'  # TLD (optional for punycode)
        r'(?::\d+)?'  # optional port
        r'(?:/\S*)?$', re.IGNORECASE)  # optional path

    if not url_pattern.match(text):
        await update.message.reply_text(
            "❌ Некорректный URL.\n\n"
            "Пожалуйста, отправьте корректный URL сайта (например: https://example.com)"
        )
        return

    # Show processing message
    await update.message.reply_text(
        "⏳ Проверяю сайт, пожалуйста подождите...\n\n"
        f"URL: {text}"
    )

    try:
        # Call API to check the site
        result = await api_client.check_site(text, user_id)

        if "error" in result:
            error_data = result["error"]
            error_msg = error_data.get("message", "Неизвестная ошибка")
            await update.message.reply_text(
                f"❌ Ошибка при проверке:\n{error_msg}\n\n"
                "Попробуйте позже или проверьте URL."
            )
        else:
            # Success - format and send report
            message = format_report(text, result)
            await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error checking URL {text}: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при проверке сайта.\n\n"
            f"Попробуйте перейти на https://ravishing-smile-production-dc59.up.railway.app и проверить сайт заново."
        )


def format_report(url: str, report: dict) -> str:
    """Format SEO report as Telegram message.

    Args:
        url: Checked URL
        report: SEO report data from API

    Returns:
        Formatted message string
    """
    score = report.get("score", 0)
    problems_critical = report.get("problems_critical", 0)
    problems_important = report.get("problems_important", 0)
    checks_ok = report.get("checks_ok", 0)
    
    # Determine emoji based on score
    if score >= 8.0:
        emoji = "✅"
    elif score >= 6.0:
        emoji = "⚠️"
    else:
        emoji = "❌"

    message = f"{emoji} *SEO Отчёт*\n\n"
    message += f"🔗 {url}\n"
    message += f"⭐ Оценка: {score:.1f}/10\n\n"

    # Show summary
    message += f"📊 *Итого:*\n"
    message += f"✅ Хорошо: {checks_ok}\n"
    if problems_critical > 0:
        message += f"🔴 Критичных: {problems_critical}\n"
    if problems_important > 0:
        message += f"🟡 Важных: {problems_important}\n"

    # Get detailed checks
    detailed_checks = report.get("detailed_checks", [])
    problems = [c for c in detailed_checks if c.get("status") == "problem"]
    ok_checks = [c for c in detailed_checks if c.get("status") == "ok"]
    
    # Show problems first (most important)
    if problems:
        message += f"\n🔴 *Нужно исправить:*\n"
        for check in problems:
            name = check.get("name", "")
            msg = check.get("message", "").replace("✅", "").replace("⚠️", "").replace("❌", "").strip()
            message += f"\n*{name}*\n{msg}\n"

    # Show all successful checks
    if ok_checks:
        message += f"\n✅ *Всё хорошо:*\n"
        for check in ok_checks:
            name = check.get("name", "")
            msg = check.get("message", "").replace("✅", "").replace("⚠️", "").replace("❌", "").strip()
            message += f"\n*{name}*\n{msg}\n"

    return message
