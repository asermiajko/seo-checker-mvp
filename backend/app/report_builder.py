"""Report builder - converts check results into structured report."""

from typing import Any

from app.checks.base import CheckResult


def calculate_score(checks: list[CheckResult]) -> float:
    """Calculate overall SEO score (0.0 - 10.0).

    Scoring:
    - ok: 1.0 point
    - partial: 0.5 points
    - problem/error: 0.0 points

    Args:
        checks: List of check results

    Returns:
        Score from 0.0 to 10.0
    """
    if not checks:
        return 0.0

    points = 0.0
    for check in checks:
        if check.status == "ok":
            points += 1.0
        elif check.status == "partial":
            points += 0.5

    return round((points / len(checks)) * 10, 1)


def group_by_category(checks: list[CheckResult]) -> list[dict[str, Any]]:
    """Group checks by category.

    Args:
        checks: List of check results

    Returns:
        List of category groups
    """
    categories: dict[str, list[CheckResult]] = {}

    for check in checks:
        cat = check.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(check)

    result = []
    for cat_name, cat_checks in categories.items():
        ok_count = sum(1 for c in cat_checks if c.status == "ok")
        result.append(
            {
                "name": cat_name,
                "score": ok_count,
                "total": len(cat_checks),
                "checks": [c.id for c in cat_checks],
            }
        )

    return result


def extract_top_priorities(checks: list[CheckResult]) -> list[dict[str, Any]]:
    """Extract top 3 priority issues.

    Args:
        checks: List of check results

    Returns:
        List of top priority issues
    """
    # Filter problems with severity
    problems = [c for c in checks if c.status in ("problem", "partial") and c.severity]

    # Sort by severity: critical > important > enhancement
    severity_order = {"critical": 0, "important": 1, "enhancement": 2}
    problems.sort(key=lambda c: severity_order.get(c.severity or "enhancement", 999))

    # Take top 3
    return [
        {"severity": p.severity, "title": p.name, "message": p.message, "check_id": p.id}
        for p in problems[:3]
    ]


def build_report(checks: list[CheckResult]) -> dict[str, Any]:
    """Build complete SEO report.

    Args:
        checks: List of check results

    Returns:
        Complete report dictionary
    """
    score = calculate_score(checks)
    categories = group_by_category(checks)
    priorities = extract_top_priorities(checks)

    # Count issues
    problems_critical = sum(1 for c in checks if c.severity == "critical")
    problems_important = sum(1 for c in checks if c.severity == "important")
    checks_ok = sum(1 for c in checks if c.status == "ok")

    return {
        "score": score,
        "categories": categories,
        "top_priorities": priorities,
        "summary": {
            "total_checks": len(checks),
            "checks_ok": checks_ok,
            "problems_critical": problems_critical,
            "problems_important": problems_important,
        },
    }
