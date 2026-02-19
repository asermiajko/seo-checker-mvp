"""Unit tests for report builder."""

import pytest

from app.checks.base import CheckResult
from app.report_builder import build_report, calculate_score


def test_calculate_score_all_ok() -> None:
    """Test score calculation: all checks ok."""
    checks = [
        CheckResult("id1", "Check 1", "ok", "msg"),
        CheckResult("id2", "Check 2", "ok", "msg"),
        CheckResult("id3", "Check 3", "ok", "msg"),
    ]
    score = calculate_score(checks)
    assert score == 10.0


def test_calculate_score_with_partial() -> None:
    """Test score calculation: mix of ok and partial."""
    checks = [
        CheckResult("id1", "Check 1", "ok", "msg"),
        CheckResult("id2", "Check 2", "ok", "msg"),
        CheckResult("id3", "Check 3", "partial", "msg"),
    ]
    score = calculate_score(checks)
    assert score == pytest.approx(8.3, rel=0.1)


def test_calculate_score_with_problems() -> None:
    """Test score calculation: with problems."""
    checks = [
        CheckResult("id1", "Check 1", "ok", "msg"),
        CheckResult("id2", "Check 2", "problem", "msg", "critical"),
        CheckResult("id3", "Check 3", "problem", "msg", "important"),
    ]
    score = calculate_score(checks)
    assert score == pytest.approx(3.3, rel=0.1)


def test_calculate_score_all_problem() -> None:
    """Test score calculation: all problems."""
    checks = [
        CheckResult("id1", "Check 1", "problem", "msg", "critical"),
        CheckResult("id2", "Check 2", "problem", "msg", "critical"),
    ]
    score = calculate_score(checks)
    assert score == 0.0


def test_build_report_structure() -> None:
    """Test report structure."""
    checks = [
        CheckResult("tech-robots", "Robots.txt", "ok", "✅ OK", category="technical"),
        CheckResult("tech-sitemap", "Sitemap", "partial", "⚠️ Partial", "important", "technical"),
        CheckResult("content-meta", "Meta", "problem", "❌ Problem", "critical", "content"),
    ]

    report = build_report(checks)

    assert "score" in report
    assert "categories" in report
    assert "top_priorities" in report
    assert "summary" in report

    assert isinstance(report["categories"], list)
    assert len(report["categories"]) == 2  # technical + content

    assert isinstance(report["top_priorities"], list)
    assert len(report["top_priorities"]) <= 3
