"""Meta tags check implementation."""

import httpx
from bs4 import BeautifulSoup

from .base import CheckResult


async def check_meta_tags(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check meta tags (title and description).

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
                id="content-meta",
                name="Meta Tags",
                status="error",
                message="⚠️ Не удалось загрузить главную страницу",
            )

        soup = BeautifulSoup(response.content, "html.parser")

        # Check title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else ""
        title_len = len(title)

        # Check description
        desc_tag = soup.find("meta", {"name": "description"})
        description = (
            str(desc_tag.get("content", "")).strip()
            if desc_tag and hasattr(desc_tag, "get")
            else ""
        )
        desc_len = len(description)

        issues = []

        # Validate title
        if not title:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="problem",
                message="❌ Title отсутствует",
                severity="critical",
            )
        elif title_len < 30:
            issues.append(f"Title короткий ({title_len} символов, рекомендуется 30-65)")
        elif title_len > 65:
            issues.append(f"Title длинный ({title_len} символов, рекомендуется 30-65)")

        # Validate description
        if not description:
            issues.append("Description отсутствует")
        elif desc_len < 120:
            issues.append(f"Description короткий ({desc_len} символов, рекомендуется 120-160)")
        elif desc_len > 160:
            issues.append(f"Description длинный ({desc_len} символов, рекомендуется 120-160)")

        if not title and not description:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="problem",
                message="❌ Title и Description отсутствуют",
                severity="critical",
            )
        elif issues:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="partial",
                message=f"⚠️ {'; '.join(issues)}",
                severity="important",
            )
        else:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="ok",
                message=f"✅ Title ({title_len} симв.) и Description ({desc_len} симв.) в норме",
            )

    except httpx.TimeoutException:
        return CheckResult(
            id="content-meta",
            name="Meta Tags",
            status="error",
            message="⚠️ Timeout при проверке meta tags",
        )
    except Exception as e:
        return CheckResult(
            id="content-meta",
            name="Meta Tags",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
        )
