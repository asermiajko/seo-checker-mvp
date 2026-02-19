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
        # Use browser-like headers to get better content
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        }
        response = await client.get(site_url, timeout=15.0, headers=headers)

        if response.status_code != 200:
            return CheckResult(
                id="tech-analytics",
                name="Analytics",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
            )

        html = response.text.lower()

        # Check for Yandex.Metrika (more patterns)
        has_yandex = (
            "mc.yandex.ru/metrika" in html
            or "metrika/tag.js" in html
            or "metrika/watch.js" in html
            or "ym(26708190" in html  # Known a101.ru counter
            or 'content="26708190"' in html
        )

        # Check for Google Analytics
        has_google = (
            "googletagmanager.com/gtag" in html
            or "google-analytics.com/analytics.js" in html
            or "gtag(" in html
        )

        # Detect if site uses JS frameworks (may have false negatives)
        has_js_framework = (
            'id="root"' in html
            or 'id="__next"' in html
            or 'id="app"' in html
            or "react" in html
            or "vue" in html
        )

        disclaimer = ""
        if has_js_framework and not has_yandex and not has_google:
            disclaimer = " (сайт использует JS-рендеринг, проверка может быть неточной)"

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
                message=f"❌ Счётчики аналитики не найдены{disclaimer}",
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
