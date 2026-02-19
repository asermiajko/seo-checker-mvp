"""Unit tests for report formatter."""


def test_format_report_high_score():
    """Test formatting report with high score (8+)."""
    from services.formatter import format_report

    report = {
        "score": 8.5,
        "problems_critical": 0,
        "problems_important": 1,
        "checks_ok": 7,
        "categories": [
            {"name": "Техническая база", "score": 5, "total": 5},
            {"name": "Контент", "score": 2, "total": 2},
        ],
        "top_priorities": [
            {
                "severity": "important",
                "title": "Description слишком короткий",
                "action": "Увеличьте до 120-160 символов",
            }
        ],
        "metadata": {
            "site_url": "https://excellent-site.ru",
            "checked_at": "2026-02-19T10:00:00",
            "execution_time_sec": 28.3,
        },
    }

    text = format_report(report)

    assert "🟢" in text
    assert "8.5/10" in text
    assert "Отлично" in text or "отлично" in text
    assert "Техническая база" in text
    assert "5/5" in text
    assert "Description слишком короткий" in text
    assert "idalite.ru" in text.lower() or "попробуйте" in text.lower()


def test_format_report_low_score():
    """Test formatting report with low score (<5)."""
    from services.formatter import format_report

    report = {
        "score": 3.5,
        "problems_critical": 3,
        "problems_important": 2,
        "checks_ok": 1,
        "categories": [
            {"name": "Техническая база", "score": 1, "total": 5},
            {"name": "Контент", "score": 0, "total": 2},
        ],
        "top_priorities": [
            {
                "severity": "critical",
                "title": "Robots.txt блокирует всё",
                "action": "Исправьте правила в robots.txt",
            },
            {
                "severity": "critical",
                "title": "Главная закрыта от индексации",
                "action": "Удалите noindex",
            },
            {
                "severity": "critical",
                "title": "Sitemap.xml не найден",
                "action": "Создайте sitemap.xml",
            },
        ],
        "metadata": {
            "site_url": "https://bad-seo.ru",
            "checked_at": "2026-02-19T11:00:00",
            "execution_time_sec": 22.1,
        },
    }

    text = format_report(report)

    assert "🔴" in text
    assert "3.5/10" in text
    assert "Критично" in text or "критично" in text
    assert "❌ Критичные проблемы: 3" in text or "❌ Критичные: 3" in text
    assert "Robots.txt блокирует всё" in text
    assert "серьёзн" in text.lower() or "оптимиз" in text.lower()


def test_format_report_medium_score():
    """Test formatting report with medium score (6-7)."""
    from services.formatter import format_report

    report = {
        "score": 6.5,
        "problems_critical": 1,
        "problems_important": 1,
        "checks_ok": 4,
        "categories": [
            {"name": "Техническая база", "score": 3, "total": 5},
            {"name": "Контент", "score": 1, "total": 2},
        ],
        "top_priorities": [
            {
                "severity": "critical",
                "title": "Нет счётчиков аналитики",
                "action": "Установите Яндекс.Метрику или Google Analytics",
            }
        ],
        "metadata": {
            "site_url": "https://medium-site.ru",
            "checked_at": "2026-02-19T12:00:00",
            "execution_time_sec": 30.5,
        },
    }

    text = format_report(report)

    assert "🟡" in text
    assert "6.5/10" in text
    assert "Хорошо" in text or "хорошо" in text
    assert "Нет счётчиков аналитики" in text


def test_format_report_includes_all_sections():
    """Test that formatted report includes all required sections."""
    from services.formatter import format_report

    report = {
        "score": 7.0,
        "problems_critical": 1,
        "problems_important": 1,
        "checks_ok": 5,
        "categories": [{"name": "Техническая база", "score": 4, "total": 5}],
        "top_priorities": [
            {"severity": "critical", "title": "Test priority", "action": "Fix it"}
        ],
        "metadata": {
            "site_url": "https://test.ru",
            "checked_at": "2026-02-19T13:00:00",
            "execution_time_sec": 25.0,
        },
    }

    text = format_report(report)

    assert "SEO-скор" in text or "скор" in text.lower()
    assert "7.0/10" in text or "7/10" in text
    assert "Критичные" in text or "критичные" in text
    assert "Важные" in text or "важные" in text
    assert "категори" in text.lower()
    assert "Техническая база" in text
    assert "проблем" in text.lower()
    assert "Test priority" in text
    assert "━" in text or "—" in text or "-" in text


def test_format_report_no_priorities():
    """Test formatting report when no priorities (perfect score)."""
    from services.formatter import format_report

    report = {
        "score": 10.0,
        "problems_critical": 0,
        "problems_important": 0,
        "checks_ok": 8,
        "categories": [
            {"name": "Техническая база", "score": 5, "total": 5},
            {"name": "Контент", "score": 2, "total": 2},
        ],
        "top_priorities": [],
        "metadata": {
            "site_url": "https://perfect-site.ru",
            "checked_at": "2026-02-19T14:00:00",
            "execution_time_sec": 20.0,
        },
    }

    text = format_report(report)

    assert "🟢" in text
    assert "10.0/10" in text or "10/10" in text
    assert "✅" in text
    assert "отлично" in text.lower() or "идеально" in text.lower()
