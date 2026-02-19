"""Telegram bot main entry point."""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler

from handlers.start import start_command
from handlers.help import help_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    logger.info(f"🤖 Bot starting... API URL: {API_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
