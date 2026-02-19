"""Start command handler for SEO Checker bot."""

import base64
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes

from services.api_client import APIClient

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")
api_client = APIClient(api_url=API_URL)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with optional deep link.

    Args:
        update: Telegram update object
        context: Bot context with args

    Deep link format: /start check_BASE64_ENCODED_URL
    Example: /start check_aHR0cHM6Ly9leGFtcGxlLnJ1
    """
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "👋 Привет! Я проверяю SEO сайтов застройщиков.\n\n"
            "Чтобы проверить сайт:\n"
            "1. Перейдите на https://checker.idalite.ru\n"
            "2. Введите URL сайта\n"
            "3. Вернитесь сюда за результатом\n\n"
            "Или отправьте мне URL прямо сейчас."
        )
        return

    arg = context.args[0]

    if not arg.startswith("check_"):
        await update.message.reply_text(
            "❌ Некорректный формат команды.\n\n"
            "Используйте форму на https://checker.idalite.ru"
        )
        return

    try:
        encoded_url = arg.replace("check_", "")
        site_url = base64.b64decode(encoded_url).decode("utf-8")

        logger.info(f"User {user_id} checking site: {site_url}")

        await update.message.reply_text(
            f"⏳ Проверяю сайт {site_url}...\n\nЭто займёт ~30 секунд."
        )

        result = await api_client.check_site(site_url, user_id)

        if "error" in result:
            await update.message.reply_text(
                f"⚠️ {result['error'].get('message', 'Произошла ошибка')}"
            )
        else:
            from services.formatter import format_report

            report_text = format_report(result)
            await update.message.reply_text(report_text, parse_mode="Markdown")

    except (ValueError, UnicodeDecodeError) as e:
        logger.error(f"Invalid Base64 encoding: {e}")
        await update.message.reply_text(
            "❌ Некорректная ссылка.\n\n"
            "Попробуйте перейти на https://checker.idalite.ru и проверить сайт заново."
        )
    except Exception as e:
        logger.error(f"Unexpected error in start_command: {e}", exc_info=True)
        await update.message.reply_text(
            "⚠️ Произошла непредвиденная ошибка. Попробуйте позже."
        )
