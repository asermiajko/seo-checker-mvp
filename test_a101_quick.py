#!/usr/bin/env python3
"""Quick test for a101.ru SEO checks (improved version)."""

import asyncio

import httpx

from backend.app.checks.analytics import check_analytics
from backend.app.checks.check_opengraph import check_opengraph
from backend.app.checks.sitemap_xml import check_sitemap_xml


async def main():
    """Test improved checks on a101.ru."""
    site_url = "https://a101.ru"

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        print(f"🔍 Testing improved checks on {site_url}\n")

        # Test Sitemap
        print("1. Testing Sitemap.xml...")
        sitemap_result, urls = await check_sitemap_xml(site_url, client)
        print(f"   Status: {sitemap_result.status}")
        print(f"   Message: {sitemap_result.message}")
        print(f"   URLs found: {len(urls)}\n")

        # Test Analytics
        print("2. Testing Analytics...")
        analytics_result = await check_analytics(site_url, client)
        print(f"   Status: {analytics_result.status}")
        print(f"   Message: {analytics_result.message}\n")

        # Test OpenGraph
        print("3. Testing OpenGraph...")
        og_result = await check_opengraph(site_url, client)
        print(f"   Status: {og_result.status}")
        print(f"   Message: {og_result.message}\n")

        # Summary
        print("=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(f"Sitemap: {'✅' if sitemap_result.status == 'ok' else '❌'}")
        print(f"Analytics: {'✅' if analytics_result.status == 'ok' else '❌'}")
        print(f"OpenGraph: {'✅' if og_result.status == 'ok' else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())
