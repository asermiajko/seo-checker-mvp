# MVP Checks - Detailed Specifications

**Module**: Checks  
**Version**: MVP (v1.0)  
**Last Updated**: 2026-02-18

---

## Overview

This document specifies the **6-8 checks** to be implemented in the MVP version.

**Design Principles**:
- ✅ No Playwright (no browser automation)
- ✅ No LLM (no AI API calls)
- ✅ Fast (each check < 10 sec)
- ✅ Simple HTTP + HTML parsing only

---

## Check 1: Robots.txt

### Specification

**ID**: `tech-robots`  
**Name**: Robots.txt Check  
**Category**: Technical Base  
**Priority**: Must-have  
**Complexity**: Low

### What It Checks

1. File exists at `{site_url}/robots.txt`
2. File is not empty
3. Contains `User-agent:` directive
4. Contains `Sitemap:` directive (optional, but recommended)

### Success Criteria

- **Status `ok`**: File exists, has User-agent and Sitemap
- **Status `partial`**: File exists, has User-agent, but no Sitemap
- **Status `problem`**: File missing or empty

### Implementation

```python
async def check_robots_txt(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check robots.txt presence and content."""
    url = f"{site_url}/robots.txt"
    
    try:
        response = await client.get(url, timeout=5.0)
        
        if response.status_code != 200:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="problem",
                message="❌ Файл robots.txt не найден",
                severity="critical"
            )
        
        content = response.text.lower()
        
        has_user_agent = "user-agent:" in content
        has_sitemap = "sitemap:" in content
        
        if has_user_agent and has_sitemap:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="ok",
                message="✅ Файл найден, содержит User-agent и Sitemap"
            )
        elif has_user_agent:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="partial",
                message="⚠️ Файл найден, но отсутствует Sitemap",
                severity="important"
            )
        else:
            return CheckResult(
                id="tech-robots",
                name="Robots.txt",
                status="problem",
                message="❌ Файл найден, но отсутствует User-agent",
                severity="critical"
            )
    
    except Exception as e:
        return CheckResult(
            id="tech-robots",
            name="Robots.txt",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}"
        )
```

### Test Cases

1. **Valid robots.txt**: Status `ok`
2. **Missing sitemap**: Status `partial`
3. **404 Not Found**: Status `problem`
4. **Empty file**: Status `problem`
5. **Timeout**: Status `error`

---

## Check 2: Sitemap.xml

### Specification

**ID**: `tech-sitemap`  
**Name**: Sitemap.xml Check  
**Category**: Technical Base  
**Priority**: Must-have  
**Complexity**: Low

### What It Checks

1. File exists at `{site_url}/sitemap.xml`
2. File is valid XML
3. Contains `<url>` or `<sitemap>` tags (sitemap index)
4. Has at least 1 URL

### Success Criteria

- **Status `ok`**: Valid sitemap with URLs
- **Status `partial`**: File exists but issues (e.g., sitemap index without checking children)
- **Status `problem`**: File missing or invalid XML

### Implementation

```python
import xml.etree.ElementTree as ET

async def check_sitemap_xml(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check sitemap.xml presence and validity."""
    url = f"{site_url}/sitemap.xml"
    
    try:
        response = await client.get(url, timeout=10.0)
        
        if response.status_code != 200:
            return CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="problem",
                message="❌ Файл sitemap.xml не найден",
                severity="critical"
            )
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Check for URLs or sitemap index
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('.//ns:url', namespaces)
        sitemaps = root.findall('.//ns:sitemap', namespaces)
        
        if urls:
            count = len(urls)
            return CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="ok",
                message=f"✅ Файл найден, содержит {count} URL"
            )
        elif sitemaps:
            count = len(sitemaps)
            return CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="partial",
                message=f"⚠️ Найден sitemap index с {count} картами (не проверяем вложенные)",
                severity="enhancement"
            )
        else:
            return CheckResult(
                id="tech-sitemap",
                name="Sitemap.xml",
                status="problem",
                message="❌ Файл найден, но не содержит URL",
                severity="important"
            )
    
    except ET.ParseError:
        return CheckResult(
            id="tech-sitemap",
            name="Sitemap.xml",
            status="problem",
            message="❌ Файл найден, но невалидный XML",
            severity="critical"
        )
    except Exception as e:
        return CheckResult(
            id="tech-sitemap",
            name="Sitemap.xml",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}"
        )
```

### Test Cases

1. **Valid sitemap with URLs**: Status `ok`
2. **Sitemap index**: Status `partial`
3. **404 Not Found**: Status `problem`
4. **Invalid XML**: Status `problem`
5. **Empty sitemap**: Status `problem`

---

## Check 3: Noindex on Main Page

### Specification

**ID**: `tech-noindex`  
**Name**: Noindex Check  
**Category**: Technical Base  
**Priority**: Must-have  
**Complexity**: Low

### What It Checks

1. Fetch main page HTML
2. Check for `<meta name="robots" content="noindex">`
3. Check for `<meta name="robots" content="noindex, nofollow">`

### Success Criteria

- **Status `ok`**: No noindex meta tag
- **Status `problem`**: Noindex found (critical error!)

### Implementation

```python
from bs4 import BeautifulSoup

async def check_noindex(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check if main page has noindex meta tag."""
    try:
        response = await client.get(site_url, timeout=10.0)
        
        if response.status_code != 200:
            return CheckResult(
                id="tech-noindex",
                name="Noindex Check",
                status="error",
                message=f"⚠️ Главная страница недоступна (HTTP {response.status_code})"
            )
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all meta robots tags
        meta_robots = soup.find_all('meta', attrs={'name': 'robots'})
        
        for meta in meta_robots:
            content = meta.get('content', '').lower()
            if 'noindex' in content:
                return CheckResult(
                    id="tech-noindex",
                    name="Noindex Check",
                    status="problem",
                    message="❌ Главная страница закрыта от индексации (noindex)",
                    severity="critical"
                )
        
        return CheckResult(
            id="tech-noindex",
            name="Noindex Check",
            status="ok",
            message="✅ Главная страница открыта для индексации"
        )
    
    except Exception as e:
        return CheckResult(
            id="tech-noindex",
            name="Noindex Check",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}"
        )
```

### Test Cases

1. **No noindex**: Status `ok`
2. **Noindex found**: Status `problem` (critical)
3. **Noindex, nofollow**: Status `problem` (critical)
4. **X-Robots-Tag header**: Also check HTTP headers (bonus)
5. **Page unreachable**: Status `error`

---

## Check 4: Meta Tags (Title & Description)

### Specification

**ID**: `content-meta`  
**Name**: Meta Tags Check  
**Category**: Content  
**Priority**: Must-have  
**Complexity**: Low

### What It Checks

1. **Title**:
   - Exists
   - Length: 30-65 characters (optimal)
   
2. **Description**:
   - Exists
   - Length: 120-160 characters (optimal)

### Success Criteria

- **Status `ok`**: Both present and optimal length
- **Status `partial`**: Present but sub-optimal length
- **Status `problem`**: Missing or very short

### Implementation

```python
async def check_meta_tags(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check title and description meta tags."""
    try:
        response = await client.get(site_url, timeout=10.0)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else None
        title_len = len(title) if title else 0
        
        # Check description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        desc = desc_tag.get('content', '').strip() if desc_tag else None
        desc_len = len(desc) if desc else 0
        
        issues = []
        
        # Validate title
        if not title:
            issues.append("❌ Title отсутствует")
        elif title_len < 30:
            issues.append(f"⚠️ Title слишком короткий ({title_len} символов, рекомендуется 30-65)")
        elif title_len > 65:
            issues.append(f"⚠️ Title слишком длинный ({title_len} символов, рекомендуется 30-65)")
        
        # Validate description
        if not desc:
            issues.append("❌ Description отсутствует")
        elif desc_len < 120:
            issues.append(f"⚠️ Description короткий ({desc_len} символов, рекомендуется 120-160)")
        elif desc_len > 160:
            issues.append(f"⚠️ Description длинный ({desc_len} символов, рекомендуется 120-160)")
        
        if not issues:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="ok",
                message="✅ Title и Description в норме"
            )
        elif len(issues) == 1 and "⚠️" in issues[0]:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="partial",
                message=issues[0],
                severity="important"
            )
        else:
            return CheckResult(
                id="content-meta",
                name="Meta Tags",
                status="problem",
                message="\n".join(issues),
                severity="critical" if "❌" in str(issues) else "important"
            )
    
    except Exception as e:
        return CheckResult(
            id="content-meta",
            name="Meta Tags",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}"
        )
```

### Test Cases

1. **Optimal title & description**: Status `ok`
2. **Missing title**: Status `problem` (critical)
3. **Short title**: Status `partial`
4. **Long description**: Status `partial`
5. **Both missing**: Status `problem` (critical)

---

## Check 5: H1/H2 Structure

### Specification

**ID**: `content-headings`  
**Name**: Headings Check  
**Category**: Content  
**Priority**: Must-have  
**Complexity**: Low

### What It Checks

1. **H1**: Exactly 1 H1 on main page
2. **H2**: At least 1 H2 on main page

### Success Criteria

- **Status `ok`**: 1 H1 + at least 1 H2
- **Status `partial`**: Has H1 but no H2, or 2+ H1
- **Status `problem`**: No H1

### Implementation

```python
async def check_headings(site_url: str, client: httpx.AsyncClient) -> CheckResult:
    """Check H1 and H2 structure."""
    try:
        response = await client.get(site_url, timeout=10.0)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        
        h1_count = len(h1_tags)
        h2_count = len(h2_tags)
        
        if h1_count == 0:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="problem",
                message="❌ H1 отсутствует на главной странице",
                severity="critical"
            )
        elif h1_count > 1:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="partial",
                message=f"⚠️ Найдено {h1_count} H1 (должен быть 1)",
                severity="important"
            )
        elif h2_count == 0:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="partial",
                message="⚠️ Есть H1, но нет H2 (рекомендуется добавить)",
                severity="enhancement"
            )
        else:
            return CheckResult(
                id="content-headings",
                name="Headings",
                status="ok",
                message=f"✅ Структура в порядке (1 H1, {h2_count} H2)"
            )
    
    except Exception as e:
        return CheckResult(
                id="content-headings",
            name="Headings",
            status="error",
            message=f"⚠️ Ошибка проверки: {str(e)}"
        )
```

---

## Check 6: Analytics Counters

### Specification

**ID**: `tech-analytics`  
**Name**: Analytics Check  
**Category**: Technical Base  
**Priority**: Must-have  
**Complexity**: Low

### What It Checks

1. **Яндекс.Метрика**: Look for `mc.yandex.ru/metrika` in HTML
2. **Google Analytics**: Look for `googletagmanager.com/gtag` or `google-analytics.com/analytics.js`

### Success Criteria

- **Status `ok`**: At least one counter found
- **Status `problem`**: No counters

---

## Check 7: HTML Sitemap (Optional)

**ID**: `structure-html-sitemap`  
**Status**: Optional for 8-check MVP

### What It Checks

1. Page exists at `{site_url}/sitemap/` or `{site_url}/sitemap.html`
2. Contains links (at least 5)

---

## Check 8: OpenGraph Tags (Optional)

**ID**: `social-opengraph`  
**Status**: Optional for 8-check MVP

### What It Checks

1. `og:title`
2. `og:description`
3. `og:image`
4. `og:url`

---

## Summary Table

| Check | Complexity | Time (impl) | Test Cases |
|-------|------------|-------------|------------|
| Robots.txt | Low | 1 hour | 5 |
| Sitemap.xml | Low | 1.5 hours | 5 |
| Noindex | Low | 1 hour | 5 |
| Meta Tags | Low | 1.5 hours | 5 |
| Headings | Low | 1 hour | 4 |
| Analytics | Low | 1 hour | 4 |
| HTML Sitemap | Medium | 1.5 hours | 4 |
| OpenGraph | Medium | 1 hour | 4 |
| **TOTAL** | | **9-11 hours** | **36 tests** |

---

## Next Steps

1. Review these specifications
2. Proceed to [testing/strategy.md](../testing/strategy.md)
3. Create implementation tasks in `/tasks`

---

**Related Documents**:
- [Checks Overview](./README.md)
- [Future Checks](./future-checks.md)
- [Testing Strategy](../testing/strategy.md)
- [API Contracts](../api/contracts.md)
