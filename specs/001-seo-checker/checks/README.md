# SEO Checks - Overview

**Module**: Checks  
**Last Updated**: 2026-02-18

---

## Overview

This module documents all SEO checks performed by the system. Checks are split into:

1. **MVP Checks** (6-8 checks) — Implemented in first version
2. **Future Checks** (5 additional) — Deferred to v1.1+

---

## MVP Checks (6-8 total)

These checks are **simple, fast, and high-value**. No Playwright, no LLM.

| # | Check ID | Name | Category | Complexity | Priority |
|---|----------|------|----------|------------|----------|
| 1 | `tech-robots` | Robots.txt | Technical | Low | Must-have |
| 2 | `tech-sitemap` | Sitemap.xml | Technical | Low | Must-have |
| 3 | `tech-noindex` | Noindex Check | Technical | Low | Must-have |
| 4 | `content-meta` | Title/Description | Content | Low | Must-have |
| 5 | `content-headings` | H1/H2 Structure | Content | Low | Must-have |
| 6 | `tech-analytics` | Analytics Counters | Technical | Low | Must-have |
| 7 | `structure-html-sitemap` | HTML Sitemap | Structure | Medium | Nice-to-have |
| 8 | `social-opengraph` | OpenGraph Tags | Social | Medium | Nice-to-have |

**Total implementation time**: 8-12 hours (with TDD)

See [mvp-checks.md](./mvp-checks.md) for detailed specifications.

---

## Future Checks (v1.1+)

These checks are **complex, slow, or require external services** (Playwright, LLM).

| # | Check ID | Name | Category | Why Deferred |
|---|----------|------|----------|--------------|
| 9 | `tech-speed` | FCP (Speed) | Technical | Requires Playwright (resource-heavy) |
| 10 | `structure-filters` | Filter Pages (LLM) | Structure | Requires LLM API (cost, complexity) |
| 11 | `seo-local` | Local SEO (LLM) | SEO | Requires LLM API |
| 12 | `seo-schema` | Schema.org | SEO | Requires checking 15 pages (slow) |
| 13 | `seo-canonical` | Canonical Tags | SEO | Requires checking 15 pages |

**Total implementation time**: 15-20 hours (with TDD)

See [future-checks.md](./future-checks.md) for detailed specifications.

---

## Check Categories

### 1. Technical Base (5 checks)
**Description**: Fundamental technical SEO (robots, sitemap, indexing, analytics)

**MVP**:
- ✅ Robots.txt
- ✅ Sitemap.xml
- ✅ Noindex check
- ✅ Analytics counters

**v1.1**:
- ⏭️ FCP (speed)

**Score Weight**: 40% of total score

---

### 2. Content (2 checks)
**Description**: On-page content optimization (meta tags, headings)

**MVP**:
- ✅ Title/Description
- ✅ H1/H2 structure

**Score Weight**: 20% of total score

---

### 3. Structure (2 checks)
**Description**: Site architecture and navigation

**MVP**:
- ⚠️ HTML sitemap (optional)

**v1.1**:
- ⏭️ Filter pages (LLM)

**Score Weight**: 15% of total score

---

### 4. SEO Enhancements (3 checks)
**Description**: Advanced SEO features (schema, canonical, local)

**v1.1 only**:
- ⏭️ Schema.org
- ⏭️ Canonical tags
- ⏭️ Local SEO

**Score Weight**: 15% of total score

---

### 5. Social (1 check)
**Description**: Social media optimization

**MVP**:
- ⚠️ OpenGraph (optional)

**Score Weight**: 10% of total score

---

## Check Status Types

Each check returns one of:

| Status | Description | Score Impact |
|--------|-------------|--------------|
| `ok` | Check passed | +1.0 |
| `partial` | Partial success | +0.5 |
| `problem` | Check failed | +0.0 |
| `error` | Technical error (site unreachable, timeout) | +0.0 |

---

## Severity Levels

Problems are classified by severity:

| Severity | Description | Examples |
|----------|-------------|----------|
| `critical` | Blocks indexing or causes major issues | Noindex on main page, no robots.txt |
| `important` | Hurts SEO significantly | Missing title, no H1 |
| `enhancement` | Nice to have, minor impact | No HTML sitemap |

---

## Score Calculation

```python
total_checks = len(checks)
ok_count = sum(1 for c in checks if c.status == "ok")
partial_count = sum(1 for c in checks if c.status == "partial")

score = (ok_count * 1.0 + partial_count * 0.5) / total_checks * 10
# Example: 5 ok + 1 partial + 2 problem = (5*1.0 + 1*0.5) / 8 * 10 = 6.9/10
```

**Score Interpretation**:
- `0-3`: 🔴 Критично (сайт не индексируется)
- `4-6`: 🟡 Плохо (много проблем)
- `7-8`: 🟢 Хорошо (базовое SEO в порядке)
- `9-10`: ✅ Отлично (профессиональный уровень)

---

## Implementation Order

For TDD implementation, follow this order:

1. **robots.txt** (simplest, no HTML parsing)
2. **sitemap.xml** (XML parsing)
3. **analytics** (HTML parsing, simple regex)
4. **noindex** (HTML meta tags)
5. **meta tags** (HTML meta tags, length checks)
6. **headings** (HTML structure)
7. **html sitemap** (link crawling)
8. **opengraph** (HTML meta tags)

**Rationale**: Start simple, gradually increase complexity.

---

## Testing Strategy

### Unit Tests (per check)
- Test with mock HTML/XML responses
- Test edge cases (missing files, malformed HTML)
- Test timeouts and errors

### Integration Tests
- Test with real HTML fixtures
- Test parallel execution (asyncio.gather)

### E2E Tests
- Test with real websites
- Test full API flow

See [testing/strategy.md](../testing/strategy.md) for details.

---

## Common Patterns

All checks follow this interface:

```python
async def check_something(site_url: str, http_client: httpx.AsyncClient) -> CheckResult:
    """
    Check something about the site.
    
    Args:
        site_url: Site URL (e.g., "https://example.ru")
        http_client: Async HTTP client
        
    Returns:
        CheckResult with status, message, severity
        
    Raises:
        CheckTimeoutError: If check takes > 10 sec
    """
    try:
        # 1. Fetch resource
        response = await http_client.get(f"{site_url}/resource", timeout=10.0)
        
        # 2. Parse content
        # ... parsing logic ...
        
        # 3. Validate
        if condition:
            return CheckResult(
                id="check-id",
                name="Check Name",
                status="ok",
                message="✅ Всё в порядке"
            )
        else:
            return CheckResult(
                id="check-id",
                name="Check Name", 
                status="problem",
                message="❌ Проблема",
                severity="critical"
            )
            
    except httpx.TimeoutException:
        raise CheckTimeoutError()
    except Exception as e:
        return CheckResult(
            id="check-id",
            name="Check Name",
            status="error",
            message=f"⚠️ Ошибка: {str(e)}"
        )
```

---

## Next Steps

1. Read [mvp-checks.md](./mvp-checks.md) for MVP check specifications
2. Read [future-checks.md](./future-checks.md) for v1.1 roadmap
3. Proceed to implementation planning

---

**Related Documents**:
- [MVP Checks Details](./mvp-checks.md)
- [Future Checks Details](./future-checks.md)
- [Testing Strategy](../testing/strategy.md)
- [API Contracts](../api/contracts.md)
