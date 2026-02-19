"""Schema.org microdata check implementation."""

import json
import random
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup

from .base import CheckResult


async def check_schema_microdata(
    site_url: str, sitemap_urls: List[str], client: httpx.AsyncClient
) -> CheckResult:
    """Check Schema.org microdata on 15 pages.

    Args:
        site_url: Website main URL
        sitemap_urls: List of URLs from sitemap
        client: Async HTTP client

    Returns:
        CheckResult with status ok/partial/problem/error
    """
    try:
        # Select 15 pages: main + 14 random from sitemap
        pages_to_check = [site_url]
        if sitemap_urls:
            sample_size = min(14, len(sitemap_urls))
            pages_to_check.extend(random.sample(sitemap_urls, sample_size))
        
        # Check each page for Schema.org
        all_schemas: Dict[str, int] = {}
        pages_checked = 0
        
        for url in pages_to_check:
            try:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    
                    # Find all LD+JSON scripts
                    for script in soup.find_all("script", type="application/ld+json"):
                        try:
                            data = json.loads(script.string)
                            
                            # Handle both single objects and arrays
                            if isinstance(data, list):
                                for item in data:
                                    schema_type = item.get("@type", "Unknown")
                                    all_schemas[schema_type] = all_schemas.get(schema_type, 0) + 1
                            else:
                                schema_type = data.get("@type", "Unknown")
                                all_schemas[schema_type] = all_schemas.get(schema_type, 0) + 1
                        except (json.JSONDecodeError, AttributeError):
                            pass
                    
                    pages_checked += 1
            except (httpx.TimeoutException, httpx.HTTPError):
                continue
        
        if pages_checked == 0:
            return CheckResult(
                id="meta-schema",
                name="Микроразметка Schema.org",
                status="error",
                message="⚠️ Не удалось проверить страницы",
                category="content",
            )
        
        # Check for key schema types
        has_organization = (
            "Organization" in all_schemas or "RealEstateAgent" in all_schemas
        )
        has_apartment_complex = "ApartmentComplex" in all_schemas
        has_product = "Product" in all_schemas
        has_breadcrumb = "BreadcrumbList" in all_schemas
        
        schema_count = len(all_schemas)
        key_schemas_count = sum([
            has_organization,
            has_apartment_complex,
            has_product,
            has_breadcrumb
        ])
        
        # Build message
        schemas_list = ", ".join(all_schemas.keys()) if all_schemas else "не найдено"
        
        # Evaluate
        if schema_count == 0:
            return CheckResult(
                id="meta-schema",
                name="Микроразметка Schema.org",
                status="problem",
                message=f"❌ Микроразметка отсутствует (проверено {pages_checked} страниц)",
                severity="important",
                category="content",
            )
        elif has_organization and key_schemas_count >= 2:
            return CheckResult(
                id="meta-schema",
                name="Микроразметка Schema.org",
                status="ok",
                message=f"✅ Микроразметка настроена ({schema_count} типов): {schemas_list}",
                category="content",
            )
        elif has_organization:
            return CheckResult(
                id="meta-schema",
                name="Микроразметка Schema.org",
                status="partial",
                message=f"⚠️ Есть Organization, но мало типов ({schema_count}): {schemas_list}",
                severity="important",
                category="content",
            )
        else:
            return CheckResult(
                id="meta-schema",
                name="Микроразметка Schema.org",
                status="partial",
                message=f"⚠️ Разметка неполная, нет Organization ({schema_count} типов): {schemas_list}",
                severity="important",
                category="content",
            )
            
    except Exception as e:
        return CheckResult(
            id="meta-schema",
            name="Микроразметка Schema.org",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
            category="content",
        )
