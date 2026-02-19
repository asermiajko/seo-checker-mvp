"""Analytics counters check implementation."""

import httpx

from .base import CheckResult


async def check_analytics(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check for analytics counters (Yandex.Metrika, Google Analytics).

    Args:
        site_url: Website URL to check
        client: Async HTTP client

    Returns:
        CheckResult with status ok/problem/error
    """
    try:
        response = await client.get(site_url, timeout=10.0)

        if response.status_code != 200:
            return CheckResult(
                id="tech-analytics",
                name="Analytics",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
            )

        html = response.text.lower()

        # Check for Yandex.Metrika
        has_yandex = "mc.yandex.ru/metrika" in html or "metrika/tag.js" in html

        # Check for Google Analytics
        has_google = (
            "googletagmanager.com/gtag" in html
            or "google-analytics.com/analytics.js" in html
            or "gtag(" in html
        )

        if has_yandex and has_google:
            return CheckResult(
                id="tech-analytics",
                name="Analytics",
                status="ok",
                message="✅ Установлены: Yandex.Metrika и Google Analytics",
            )
        elif has_yandex:
            return CheckResult(
                id="tech-analytics",
                name="Analytics",
                status="ok",
                message="✅ Установлена Yandex.Metrika",
            )
        elif has_google:
            return CheckResult(
                id="tech-analytics",
                name="Analytics",
                status="ok",
                message="✅ Установлен Google Analytics",
            )
        else:
            return CheckResult(
                id="tech-analytics",
                name="Analytics",
                status="problem",
                message="❌ Счётчики аналитики не найдены",
                severity="important",
            )

    except httpx.TimeoutException:
        return CheckResult(
            id="tech-analytics",
            name="Analytics",
            status="error",
            message="⚠️ Timeout при проверке аналитики",
        )
    except Exception as e:
        return CheckResult(
            id="tech-analytics",
            name="Analytics",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
        )
