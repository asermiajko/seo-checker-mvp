"""Report formatter for Telegram messages."""

from typing import Any


def get_category_emoji(category_name: str) -> str:
    """Get emoji for category.

    Args:
        category_name: Name of the category

    Returns:
        str: Emoji for the category
    """
    emojis = {
        "Техническая база": "⚙️",
        "Контент": "📝",
        "Структура": "🏗",
        "SEO улучшения": "🔍",
        "Социальные сети": "📱",
    }
    return emojis.get(category_name, "📊")


def format_report(report: dict[str, Any]) -> str:
    """Convert API response to Telegram Markdown formatted message.

    Args:
        report: API response dictionary with score, categories, priorities

    Returns:
        str: Formatted report message for Telegram
    """
    score = report["score"]

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

    text = f"{emoji} **SEO-скор: {score}/10** ({level})\n\n"
    text += "━━━━━━━━━━━━━━━━\n\n"

    text += "📊 **Результаты:**\n"
    text += f"❌ Критичные проблемы: {report['problems_critical']}\n"
    text += f"⚠️ Важные: {report['problems_important']}\n"
    text += f"✅ Всё хорошо: {report['checks_ok']}\n\n"
    text += "━━━━━━━━━━━━━━━━\n\n"

    text += "📂 **По категориям:**\n"
    for cat in report["categories"]:
        cat_emoji = get_category_emoji(cat["name"])
        text += f"{cat_emoji} {cat['name']}: {cat['score']}/{cat['total']}\n"
    text += "\n━━━━━━━━━━━━━━━━\n\n"

    if report.get("top_priorities"):
        text += "🚨 **Топ проблемы:**\n\n"
        for i, priority in enumerate(report["top_priorities"][:3], 1):
            severity_emoji = "❌" if priority["severity"] == "critical" else "⚠️"
            text += f"{i}. {severity_emoji} {priority['title']}\n"
            text += f"   → {priority['action']}\n\n"
        text += "━━━━━━━━━━━━━━━━\n\n"

    if score < 5:
        text += "💡 **Ваш сайт нуждается в серьёзной оптимизации!**\n"
        text += "Ida.Lite автоматизирует SEO для застройщиков.\n\n"
        text += "🚀 [Попробовать бесплатно](https://idalite.ru)\n"
    elif score < 8:
        text += "💡 Эти проблемы решаются в Ida.Lite!\n\n"
        text += "👉 [Узнать больше](https://idalite.ru)\n"
    else:
        text += "✅ Ваш сайт в отличном состоянии!\n\n"
        text += "💡 Хотите держать SEO на автопилоте? "
        text += "[Попробуйте Ida.Lite](https://idalite.ru)\n"

    return text
