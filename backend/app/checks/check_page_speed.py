"""Page speed check implementation (FCP with Playwright)."""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from .base import CheckResult


async def check_page_speed(site_url: str) -> CheckResult:
    """Check page loading speed (First Contentful Paint).

    Uses Playwright headless browser to measure FCP on mobile device.

    Args:
        site_url: Website URL to check

    Returns:
        CheckResult with status ok/partial/problem/error
    """
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Emulate mobile device (iPhone 12)
            device = p.devices['iPhone 12']
            context = await browser.new_context(**device)
            page = await context.new_page()
            
            try:
                # Navigate to page with 10 second timeout
                await page.goto(site_url, wait_until='domcontentloaded', timeout=10000)
                
                # Measure First Contentful Paint
                fcp = await page.evaluate('''() => {
                    const paint = performance.getEntriesByType('paint')
                        .find(entry => entry.name === 'first-contentful-paint');
                    return paint ? paint.startTime / 1000 : null;
                }''')
                
                await browser.close()
                
                if fcp is None:
                    return CheckResult(
                        id="tech-speed",
                        name="Скорость загрузки",
                        status="problem",
                        message="⚠️ Не удалось измерить FCP (First Contentful Paint)",
                        severity="important",
                        category="technical",
                    )
                
                # Evaluate FCP
                if fcp < 3.0:
                    return CheckResult(
                        id="tech-speed",
                        name="Скорость загрузки",
                        status="ok",
                        message=f"✅ Быстрая загрузка: FCP {fcp:.2f} сек (< 3 сек)",
                        category="technical",
                    )
                elif fcp < 5.0:
                    return CheckResult(
                        id="tech-speed",
                        name="Скорость загрузки",
                        status="partial",
                        message=f"⚠️ Средняя скорость: FCP {fcp:.2f} сек (рекомендуется < 3 сек)",
                        severity="important",
                        category="technical",
                    )
                else:
                    return CheckResult(
                        id="tech-speed",
                        name="Скорость загрузки",
                        status="problem",
                        message=f"❌ Медленная загрузка: FCP {fcp:.2f} сек (критично > 5 сек)",
                        severity="critical",
                        category="technical",
                    )
                    
            except PlaywrightTimeout:
                await browser.close()
                return CheckResult(
                    id="tech-speed",
                    name="Скорость загрузки",
                    status="problem",
                    message="❌ Сайт не открылся за 10 секунд (timeout)",
                    severity="critical",
                    category="technical",
                )
                
    except Exception as e:
        return CheckResult(
            id="tech-speed",
            name="Скорость загрузки",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}",
            category="technical",
        )
