"""Quick test for schema check."""

import asyncio
import httpx
from backend.app.checks.check_schema import check_schema_microdata


async def test_schema():
    """Test schema check on 72dom.com."""
    site_url = "https://72dom.com"
    sitemap_urls = [
        "https://72dom.com/catalog/",
        "https://72dom.com/about/",
    ]
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        result = await check_schema_microdata(site_url, sitemap_urls, client)
        
        print(f"ID: {result.id}")
        print(f"Name: {result.name}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        print(f"Category: {result.category}")
        print(f"Severity: {result.severity}")


if __name__ == "__main__":
    asyncio.run(test_schema())
