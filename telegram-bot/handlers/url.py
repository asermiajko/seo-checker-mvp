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

    # Validate URL format
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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
        result = await api_client.check_url(text, user_id)

        if result.get("status") == "success":
            report = result.get("report", {})
            
            # Format report message
            message = format_report(text, report)
            await update.message.reply_text(message, parse_mode="Markdown")
        else:
            error_msg = result.get("error", "Неизвестная ошибка")
            await update.message.reply_text(
                f"❌ Ошибка при проверке:\n{error_msg}\n\n"
                "Попробуйте позже или проверьте URL."
            )

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
        report: SEO report data

    Returns:
        Formatted message string
    """
    total = report.get("total_checks", 0)
    passed = report.get("passed_checks", 0)
    failed = report.get("failed_checks", 0)
    warnings = report.get("warnings", 0)

    score = (passed / total * 100) if total > 0 else 0

    # Determine emoji based on score
    if score >= 80:
        emoji = "✅"
    elif score >= 60:
        emoji = "⚠️"
    else:
        emoji = "❌"

    message = f"{emoji} *SEO Отчёт*\n\n"
    message += f"🔗 URL: {url}\n"
    message += f"📊 Результат: {passed}/{total} проверок пройдено\n"
    message += f"⭐ Оценка: {score:.0f}%\n\n"

    if failed > 0:
        message += f"❌ Не пройдено: {failed}\n"
    if warnings > 0:
        message += f"⚠️ Предупреждений: {warnings}\n"

    message += f"\n🔍 Детали проверки:\n"

    # Add check results
    checks = report.get("checks", {})
    for category, category_checks in checks.items():
        if isinstance(category_checks, dict):
            for check_name, check_data in category_checks.items():
                status = check_data.get("status", "unknown")
                if status == "passed":
                    message += f"✅ {check_name}\n"
                elif status == "failed":
                    message += f"❌ {check_name}\n"
                elif status == "warning":
                    message += f"⚠️ {check_name}\n"

    message += f"\n📱 Полный отчёт: https://ravishing-smile-production-dc59.up.railway.app"

    return message
