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
        # Use browser-like headers to get better content
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        }
        response = await client.get(site_url, timeout=15.0, headers=headers)

        if response.status_code != 200:
            return CheckResult(
                id="content-opengraph",
                name="OpenGraph Tags",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
                category="content",
            )

        soup = BeautifulSoup(response.content, "html.parser")

        # Check for OpenGraph tags (try both property= and name=)
        og_title = soup.find("meta", property="og:title") or soup.find(
            "meta", attrs={"name": "og:title"}
        )
        og_description = soup.find("meta", property="og:description") or soup.find(
            "meta", attrs={"name": "og:description"}
        )
        og_image = soup.find("meta", property="og:image") or soup.find(
            "meta", attrs={"name": "og:image"}
        )

        has_title = og_title is not None
        has_description = og_description is not None
        has_image = og_image is not None

        # Detect JS frameworks
        html_lower = response.text.lower()
        has_js_framework = (
            soup.find(id="root")
            or soup.find(id="__next")
            or soup.find(id="app")
            or "react" in html_lower
            or "vue" in html_lower
        )

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
            disclaimer = (
                " (сайт может использовать JS-рендеринг)"
                if has_js_framework
                else ""
            )
            return CheckResult(
                id="content-opengraph",
                name="OpenGraph Tags",
                status="problem",
                message=f"❌ OpenGraph теги отсутствуют полностью{disclaimer}",
                severity="critical",
                category="content",
            )
        else:
            disclaimer = (
                " (сайт может использовать JS-рендеринг, проверьте вручную)"
                if has_js_framework
                else ""
            )
            return CheckResult(
                id="content-opengraph",
                name="OpenGraph Tags",
                status="partial",
                message=f"⚠️ OpenGraph: отсутствуют теги - {', '.join(missing_tags)}{disclaimer}",
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
