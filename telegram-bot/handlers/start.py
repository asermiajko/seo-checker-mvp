"""Start command handler for SEO Checker bot."""

import logging
import os
from uuid import UUID

import httpx
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with optional session deep link.

    Args:
        update: Telegram update object
        context: Bot context with args

    Deep link format: /start session_UUID
    Example: /start session_550e8400-e29b-41d4-a716-446655440000
    """
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Case 1: No arguments - just welcome message
    if not context.args:
        await update.message.reply_text(
            "👋 Привет! Я проверяю SEO сайтов застройщиков.\n\n"
            "📝 Отправьте мне URL сайта (например: https://example.com) и я проведу проверку 13 SEO-параметров.\n\n"
            "⏱ Проверка займёт ~30-60 секунд.\n\n"
            "Команды:\n"
            "/help — подробная справка"
        )
        return

    arg = context.args[0]

    # Case 2: Session deep link from web form
    if arg.startswith("session_"):
        try:
            session_id_str = arg.replace("session_", "")
            session_id = UUID(session_id_str)

            logger.info(f"User {user_id} opened bot via web session: {session_id}")

            # Update session with Telegram data
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{API_URL}/api/update-session-telegram",
                    json={
                        "session_id": str(session_id),
                        "telegram_id": user_id,
                        "telegram_username": username,
                    },
                )

                if response.status_code == 200:
                    logger.info(f"Session {session_id} updated with Telegram data")
                else:
                    logger.warning(
                        f"Failed to update session {session_id}: {response.status_code}"
                    )

            # Store session_id in user context for future checks
            context.user_data["session_id"] = str(session_id)

            await update.message.reply_text(
                "✅ Отлично! Теперь отправьте мне URL сайта для проверки.\n\n"
                "Пример: https://example.com\n\n"
                "⏱ Проверка займёт ~30-60 секунд."
            )

        except (ValueError, IndexError) as e:
            logger.error(f"Invalid session_id format: {e}")
            await update.message.reply_text(
                "❌ Некорректная ссылка.\n\n"
                "Попробуйте открыть бота заново с главной страницы."
            )

    # Case 3: Unknown argument format
    else:
        await update.message.reply_text(
            "👋 Привет! Отправьте мне URL сайта для проверки.\n\n"
            "Пример: https://example.com"
        )
