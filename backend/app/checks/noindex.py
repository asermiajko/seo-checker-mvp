"""Noindex check implementation."""

import httpx
from bs4 import BeautifulSoup

from .base import CheckResult


async def check_noindex(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check for noindex on main page.

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
                id="tech-noindex",
                name="Noindex Check",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
            )

        # Check X-Robots-Tag header
        x_robots_tag = response.headers.get("X-Robots-Tag", "").lower()
        if "noindex" in x_robots_tag:
            return CheckResult(
                id="tech-noindex",
                name="Noindex Check",
                status="problem",
                message="❌ Noindex найден в HTTP заголовке X-Robots-Tag",
                severity="critical",
            )

        # Check meta robots tag
        soup = BeautifulSoup(response.content, "html.parser")
        meta_robots = soup.find("meta", {"name": "robots"})

        if meta_robots and hasattr(meta_robots, "get"):
            content = str(meta_robots.get("content", "")).lower()
            if "noindex" in content:
                return CheckResult(
                    id="tech-noindex",
                    name="Noindex Check",
                    status="problem",
                    message="❌ Noindex найден в meta robots на главной странице",
                    severity="critical",
                )

        return CheckResult(
            id="tech-noindex",
            name="Noindex Check",
            status="ok",
            message="✅ Noindex не найден на главной странице",
        )

    except httpx.TimeoutException:
        return CheckResult(
            id="tech-noindex",
            name="Noindex Check",
            status="error",
            message="⚠️ Timeout при проверке noindex",
        )
    except Exception as e:
        return CheckResult(
            id="tech-noindex",
            name="Noindex Check",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
        )
