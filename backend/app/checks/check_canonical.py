"""Canonical URL check implementation."""

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .base import CheckResult


async def check_canonical(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check canonical URL tag on main page.

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
                id="tech-canonical",
                name="Canonical URL",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
                category="technical",
            )

        soup = BeautifulSoup(response.content, "html.parser")
        canonical = soup.find("link", rel="canonical")

        if not canonical:
            return CheckResult(
                id="tech-canonical",
                name="Canonical URL",
                status="problem",
                message="❌ Canonical URL отсутствует (может привести к дублям)",
                severity="critical",
                category="technical",
            )

        href = canonical.get("href", "")
        if not href:
            return CheckResult(
                id="tech-canonical",
                name="Canonical URL",
                status="problem",
                message="❌ Canonical URL указан, но атрибут href пуст",
                severity="critical",
                category="technical",
            )

        # Check if canonical points to the same domain
        parsed_site = urlparse(site_url)
        parsed_canonical = urlparse(href)

        if parsed_site.netloc != parsed_canonical.netloc:
            return CheckResult(
                id="tech-canonical",
                name="Canonical URL",
                status="problem",
                message=f"❌ Canonical URL указывает на другой домен: {parsed_canonical.netloc}",
                severity="critical",
                category="technical",
            )

        return CheckResult(
            id="tech-canonical",
            name="Canonical URL",
            status="ok",
            message="✅ Canonical URL установлен корректно",
            category="technical",
        )

    except httpx.TimeoutException:
        return CheckResult(
            id="tech-canonical",
            name="Canonical URL",
            status="error",
            message="⚠️ Timeout при проверке canonical URL",
            category="technical",
        )
    except Exception as e:
        return CheckResult(
            id="tech-canonical",
            name="Canonical URL",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
            category="technical",
        )
