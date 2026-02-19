"""Help command handler for SEO Checker bot."""

from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command.

    Args:
        update: Telegram update object
        context: Bot context
    """
    await update.message.reply_text(
        "ℹ️ **Как пользоваться:**\n\n"
        "1️⃣ Откройте форму: https://ravishing-smile-production-dc59.up.railway.app\n"
        "2️⃣ Введите URL сайта\n"
        "3️⃣ Получите отчёт здесь\n\n"
        "Я проверяю:\n"
        "✅ Robots.txt и Sitemap\n"
        "✅ Title и Description\n"
        "✅ Структуру заголовков\n"
        "✅ Счётчики аналитики\n"
        "✅ И ещё 2 параметра\n\n"
        "Проверка занимает ~30 секунд.",
        parse_mode="Markdown",
    )
