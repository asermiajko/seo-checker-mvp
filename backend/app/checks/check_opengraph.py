"""OpenGraph tags check implementation."""

import httpx
from bs4 import BeautifulSoup

from .base import CheckResult


async def check_opengraph(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check OpenGraph tags on main page.

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
                id="content-opengraph",
                name="OpenGraph Tags",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
                category="content",
            )

        soup = BeautifulSoup(response.content, "html.parser")

        # Check for OpenGraph tags
        og_title = soup.find("meta", property="og:title")
        og_description = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")

        has_title = og_title is not None
        has_description = og_description is not None
        has_image = og_image is not None

        present_count = sum([has_title, has_description, has_image])
        missing_tags = []

        if not has_title:
            missing_tags.append("og:title")
        if not has_description:
            missing_tags.append("og:description")
        if not has_image:
            missing_tags.append("og:image")

        if present_count == 3:
            return CheckResult(
                id="content-opengraph",
                name="OpenGraph Tags",
                status="ok",
                message="✅ OpenGraph теги настроены (title, description, image)",
                category="content",
            )
        elif present_count == 0:
            return CheckResult(
                id="content-opengraph",
                name="OpenGraph Tags",
                status="problem",
                message="❌ OpenGraph теги отсутствуют полностью",
                severity="critical",
                category="content",
            )
        else:
            return CheckResult(
                id="content-opengraph",
                name="OpenGraph Tags",
                status="partial",
                message=f"⚠️ OpenGraph: отсутствуют теги - {', '.join(missing_tags)}",
                severity="important",
                category="content",
            )

    except httpx.TimeoutException:
        return CheckResult(
            id="content-opengraph",
            name="OpenGraph Tags",
            status="error",
            message="⚠️ Timeout при проверке OpenGraph тегов",
            category="content",
        )
    except Exception as e:
        return CheckResult(
            id="content-opengraph",
            name="OpenGraph Tags",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
            category="content",
        )
