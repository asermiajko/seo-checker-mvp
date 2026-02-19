"""API routes for SEO checks."""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.checks.analytics import check_analytics
from app.checks.check_canonical import check_canonical
from app.checks.check_html_sitemap import check_html_sitemap
from app.checks.check_opengraph import check_opengraph
from app.checks.headings import check_headings
from app.checks.meta_tags import check_meta_tags
from app.checks.noindex import check_noindex
from app.checks.robots_txt import check_robots_txt
from app.checks.sitemap_xml import check_sitemap_xml
from app.database import get_db
from app.models import CheckRequest, CheckResult
from app.report_builder import build_report
from app.schemas import CheckRequestSchema, CheckResponseSchema

router = APIRouter(prefix="/api", tags=["checks"])


async def check_rate_limit(telegram_id: int, session: AsyncSession) -> None:
    """Check if user exceeded rate limit (5 checks per hour).

    Args:
        telegram_id: Telegram user ID
        session: Database session

    Raises:
        HTTPException: If rate limit exceeded
    """
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    count = await session.scalar(
        select(func.count())
        .select_from(CheckRequest)
        .where(CheckRequest.telegram_id == telegram_id)
        .where(CheckRequest.created_at > one_hour_ago)
    )

    if count and count >= 5:
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": "Вы превысили лимит проверок (5 в час). Попробуйте позже.",
                    "retry_after_sec": 3600,
                }
            },
        )


@router.post("/check", response_model=CheckResponseSchema)
async def check_site(
    request: CheckRequestSchema, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Run SEO checks for a website.

    Args:
        request: Check request with site_url and telegram_id
        db: Database session

    Returns:
        Complete SEO report with score, categories, priorities, and detailed checks

    Raises:
        HTTPException: If validation fails or rate limit exceeded
    """
    start_time = datetime.utcnow()

    # Check rate limit
    # TODO: Включить перед production релизом! (временно отключено для отладки)
    # await check_rate_limit(request.telegram_id, db)

    # Save CheckRequest to database
    check_request = CheckRequest(
        telegram_id=request.telegram_id,
        site_url=request.site_url,
        status="running",
    )
    db.add(check_request)
    await db.commit()
    await db.refresh(check_request)

    try:
        # Run all checks in parallel
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            check_results = await asyncio.gather(
                check_robots_txt(request.site_url, client),
                check_sitemap_xml(request.site_url, client),
                check_analytics(request.site_url, client),
                check_noindex(request.site_url, client),
                check_meta_tags(request.site_url, client),
                check_headings(request.site_url, client),
                check_canonical(request.site_url, client),
                check_opengraph(request.site_url, client),
                check_html_sitemap(request.site_url, client),
                return_exceptions=True,
            )

        # Filter out exceptions and convert to CheckResult
        from app.checks.base import CheckResult as CheckResultData

        valid_results: list[CheckResultData] = []
        failed_count = 0

        for result in check_results:
            if isinstance(result, Exception):
                failed_count += 1
            elif isinstance(result, CheckResultData):
                valid_results.append(result)

        # Build report
        report = build_report(valid_results)

        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds())

        # Prepare detailed checks for response
        detailed_checks = [
            {
                "id": check.id,
                "name": check.name,
                "status": check.status,
                "message": check.message,
                "category": check.category,
                "severity": check.severity,
            }
            for check in valid_results
        ]

        # Prepare response data
        response_data = {
            "score": report["score"],
            "problems_critical": report["summary"]["problems_critical"],
            "problems_important": report["summary"]["problems_important"],
            "checks_ok": report["summary"]["checks_ok"],
            "categories": report["categories"],
            "top_priorities": report["top_priorities"],
            "detailed_checks": detailed_checks,
            "metadata": {
                "checked_at": start_time.isoformat() + "Z",
                "processing_time_sec": processing_time,
                "checks_total": len(check_results),
                "checks_completed": len(valid_results),
                "checks_failed": failed_count,
            },
        }

        # Save CheckResult to database
        check_result = CheckResult(
            check_request_id=check_request.id,
            score=report["score"],
            problems_critical=report["summary"]["problems_critical"],
            problems_important=report["summary"]["problems_important"],
            checks_ok=report["summary"]["checks_ok"],
            report_data=report,
            detailed_checks=detailed_checks,
            processing_time_sec=processing_time,
        )
        db.add(check_result)

        # Update CheckRequest status
        check_request.status = "completed"  # type: ignore[assignment]
        await db.commit()

        return response_data

    except Exception as e:
        # Update CheckRequest status to failed
        check_request.status = "failed"  # type: ignore[assignment]
        await db.commit()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "internal_error",
                    "message": "Произошла внутренняя ошибка",
                }
            },
        ) from e
