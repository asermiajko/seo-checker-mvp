"""Robots.txt check implementation."""

import httpx

from .base import CheckResult


async def check_robots_txt(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check robots.txt presence and content.

    Args:
        site_url: Website URL to check
        client: Async HTTP client

    Returns:
        CheckResult with status ok/partial/problem/error
    """
    url = f"{site_url}/robots.txt"

    try:
        response = await client.get(url, timeout=5.0)

        if response.status_code != 200:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="problem",
                message="❌ Файл robots.txt не найден",
                severity="critical",
            )

        content = response.text.lower()

        has_user_agent = "user-agent:" in content
        has_sitemap = "sitemap:" in content

        if has_user_agent and has_sitemap:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="ok",
                message="✅ Файл найден, содержит User-agent и Sitemap",
            )
        elif has_user_agent:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="partial",
                message="⚠️ Файл найден, но отсутствует Sitemap",
                severity="important",
            )
        else:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="problem",
                message="❌ Файл найден, но отсутствует User-agent",
                severity="critical",
            )

    except httpx.TimeoutException:
        return CheckResult(
            id="tech-robots",
            name="Robots.txt",
            status="error",
            message="⚠️ Timeout при проверке robots.txt",
        )
    except Exception as e:
        return CheckResult(
            id="tech-robots",
            name="Robots.txt",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
        )
