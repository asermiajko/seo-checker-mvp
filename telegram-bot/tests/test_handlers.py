"""Unit tests for bot handlers."""

import base64
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from telegram import Update, User, Message


@pytest.mark.asyncio
async def test_start_command_without_args():
    """Test /start command without deep link arguments."""
    from handlers.start import start_command

    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456789
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.args = []

    await start_command(update, context)

    update.message.reply_text.assert_called_once()
    message_text = update.message.reply_text.call_args[0][0]

    assert "👋" in message_text
    assert "SEO" in message_text or "сайт" in message_text
    assert "https://checker.idalite.ru" in message_text or "URL" in message_text


@pytest.mark.asyncio
async def test_start_command_with_deep_link():
    """Test /start command with deep link (check_ENCODED_URL)."""
    from handlers.start import start_command

    test_url = "https://example.ru"
    encoded = base64.b64encode(test_url.encode()).decode()

    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 987654321
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.args = [f"check_{encoded}"]

    mock_api_response = {
        "score": 7.5,
        "problems_critical": 1,
        "problems_important": 1,
        "checks_ok": 5,
        "categories": [{"name": "Техническая база", "score": 4, "total": 5}],
        "top_priorities": [
            {
                "severity": "critical",
                "title": "Главная закрыта от индексации",
                "action": "Удалите noindex",
            }
        ],
    }

    mock_api_client = AsyncMock()
    mock_api_client.check_site = AsyncMock(return_value=mock_api_response)

    with patch("handlers.start.api_client", mock_api_client):
        await start_command(update, context)

    assert update.message.reply_text.call_count >= 2

    first_call_text = update.message.reply_text.call_args_list[0][0][0]
    assert "⏳" in first_call_text or "Проверяю" in first_call_text

    mock_api_client.check_site.assert_called_once_with(test_url, 987654321)


@pytest.mark.asyncio
async def test_start_command_handles_invalid_base64():
    """Test /start command with invalid Base64 encoding."""
    from handlers.start import start_command

    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 111111111
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.args = ["check_INVALID!!!BASE64"]

    await start_command(update, context)

    update.message.reply_text.assert_called()
    message_text = update.message.reply_text.call_args[0][0]

    assert "❌" in message_text or "ошибк" in message_text.lower()
