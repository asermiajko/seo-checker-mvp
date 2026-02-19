"""HTML sitemap check implementation."""

import httpx
from bs4 import BeautifulSoup

from .base import CheckResult


async def check_html_sitemap(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check for HTML sitemap presence.

    Args:
        site_url: Website URL to check
        client: Async HTTP client

    Returns:
        CheckResult with status ok/problem/error
    """
    urls_to_check = [
        f"{site_url}/sitemap/",
        f"{site_url}/sitemap.html",
        f"{site_url}/karta-sajta/",
        f"{site_url}/map/",
    ]

    try:
        for url in urls_to_check:
            try:
                response = await client.get(url, timeout=5.0)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    links = soup.find_all("a")

                    if len(links) >= 5:
                        # Extract path from URL for display
                        path = url.replace(site_url, "")
                        return CheckResult(
                            id="content-sitemap-html",
                            name="HTML-карта сайта",
                            status="ok",
                            message=f"✅ HTML-карта найдена ({path}), содержит {len(links)} ссылок",
                            category="content",
                        )
            except (httpx.TimeoutException, httpx.HTTPError):
                # Continue checking other URLs
                continue

        # No valid sitemap found
        return CheckResult(
            id="content-sitemap-html",
            name="HTML-карта сайта",
            status="problem",
            message="⚠️ HTML-карта сайта не найдена (проверены /sitemap/, /karta-sajta/)",
            severity="important",
            category="content",
        )

    except Exception as e:
        return CheckResult(
            id="content-sitemap-html",
            name="HTML-карта сайта",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
            category="content",
        )
