#!/usr/bin/env python3
"""Test analytics check locally to debug."""

import asyncio

import httpx


async def test_analytics_locally():
    """Test what our code actually sees."""
    site_url = "https://a101.ru"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        print(f"🔍 Fetching {site_url}")
        response = await client.get(site_url, headers=headers)

        print(f"✅ Status: {response.status_code}")
        print(f"📏 Content length: {len(response.text)} chars\n")

        html = response.text.lower()

        # Check patterns
        patterns = {
            '"mc.yandex.ru/metrika"': "mc.yandex.ru/metrika" in html,
            '"metrika/tag.js"': "metrika/tag.js" in html,
            '"metrika/watch.js"': "metrika/watch.js" in html,
            '"ym(26708190"': "ym(26708190" in html,
            "'content=\"26708190\"'": 'content="26708190"' in html,
        }

        print("🔍 Pattern Check Results:")
        for pattern, found in patterns.items():
            status = "✅" if found else "❌"
            print(f"  {status} {pattern}: {found}")

        print(f"\n📊 Overall: has_yandex = {any(patterns.values())}")


if __name__ == "__main__":
    asyncio.run(test_analytics_locally())
