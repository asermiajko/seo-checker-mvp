"""Headings check implementation."""

import httpx
from bs4 import BeautifulSoup

from .base import CheckResult


async def check_headings(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check H1 and H2 structure.

    Args:
        site_url: Website URL to check
        client: Async HTTP client

    Returns:
        CheckResult with status ok/partial/problem/error
    """
    try:
        response = await client.get(site_url, timeout=10.0)

        if response.status_code != 200:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
            )

        soup = BeautifulSoup(response.content, "html.parser")

        h1_tags = soup.find_all("h1")
        h2_tags = soup.find_all("h2")

        h1_count = len(h1_tags)
        h2_count = len(h2_tags)

        if h1_count == 0:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="problem",
                message="❌ H1 отсутствует на главной странице",
                severity="critical",
            )
        elif h1_count > 1:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="partial",
                message=f"⚠️ Найдено {h1_count} H1 (должен быть 1)",
                severity="important",
            )
        elif h2_count == 0:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="partial",
                message="⚠️ Есть H1, но нет H2 (рекомендуется добавить)",
                severity="enhancement",
            )
        else:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="ok",
                message=f"✅ Структура в порядке (1 H1, {h2_count} H2)",
            )

    except httpx.TimeoutException:
        return CheckResult(
            id="content-headings",
            name="Headings",
            status="error",
            message="⚠️ Timeout при проверке headings",
        )
    except Exception as e:
        return CheckResult(
            id="content-headings",
            name="Headings",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
        )
