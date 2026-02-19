"""Sitemap.xml check implementation."""

import xml.etree.ElementTree as ElementTree
from typing import List, Tuple

import httpx

from .base import CheckResult


async def check_sitemap_xml(
    site_url: str, client: httpx.AsyncClient
) -> Tuple[CheckResult, List[str]]:
    """Check sitemap.xml presence and validity.

    Args:
        site_url: Website URL to check
        client: Async HTTP client

    Returns:
        Tuple of (CheckResult, list of URLs from sitemap)
    """
    url = f"{site_url}/sitemap.xml"
    sitemap_urls: List[str] = []

    try:
        # Use longer timeout and browser-like headers for better compatibility
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SEOChecker/1.0; +https://seo-checker.com/bot)",
            "Accept": "application/xml,text/xml,*/*",
        }
        response = await client.get(url, timeout=15.0, headers=headers)

        if response.status_code != 200:
            return (
                CheckResult(
                    id="tech-sitemap",
                    name="Sitemap.xml",
                    status="problem",
                    message="❌ Файл sitemap.xml не найден",
                    severity="critical",
                ),
                [],
            )

        # Parse XML
        root = ElementTree.fromstring(response.content)

        # Check for URLs or sitemap index
        namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall(".//ns:url/ns:loc", namespaces)
        sitemaps = root.findall(".//ns:sitemap", namespaces)

        if urls:
            sitemap_urls = [url.text for url in urls if url.text]
            count = len(sitemap_urls)
            return (
                CheckResult(
                    id="tech-sitemap",
                    name="Sitemap.xml",
                    status="ok",
                    message=f"✅ Файл найден, содержит {count} URL",
                ),
                sitemap_urls,
            )
        elif sitemaps:
            count = len(sitemaps)
            return (
                CheckResult(
                    id="tech-sitemap",
                    name="Sitemap.xml",
                    status="partial",
                    message=f"⚠️ Найден sitemap index с {count} картами (не проверяем вложенные)",
                    severity="enhancement",
                ),
                [],
            )
        else:
            return (
                CheckResult(
                    id="tech-sitemap",
                    name="Sitemap.xml",
                    status="problem",
                    message="❌ Файл найден, но не содержит URL",
                    severity="important",
                ),
                [],
            )

    except ElementTree.ParseError:
        return (
            CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="problem",
                message="❌ Файл найден, но невалидный XML",
                severity="critical",
            ),
            [],
        )
    except httpx.TimeoutException:
        return (
            CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="error",
                message="⚠️ Timeout при проверке sitemap.xml",
            ),
            [],
        )
    except Exception as e:
        return (
            CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="error",
                message=f"⚠️ Ошибка проверки: {str(e)}",
            ),
            [],
        )
