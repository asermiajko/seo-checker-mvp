"""API routes for web session tracking."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import WebSession
from app.schemas import (
    SessionResponseSchema,
    TrackSessionRequestSchema,
    UpdateSessionTelegramSchema,
)

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/track-session", response_model=SessionResponseSchema)
async def track_session(
    request: TrackSessionRequestSchema, db: AsyncSession = Depends(get_db)
) -> dict:
    """Track web session with UTM parameters.

    Args:
        request: Session tracking data with UTM params
        db: Database session

    Returns:
        Session confirmation with status

    Raises:
        HTTPException: If session creation fails
    """
    # Check if session already exists
    existing_session = await db.scalar(
        select(WebSession).where(WebSession.session_id == request.session_id)
    )

    if existing_session:
        return {
            "session_id": request.session_id,
            "status": "updated",
            "message": "Session already exists",
        }

    # Create new session
    new_session = WebSession(
        session_id=request.session_id,
        utm_source=request.utm_source,
        utm_medium=request.utm_medium,
        utm_campaign=request.utm_campaign,
        utm_term=request.utm_term,
        utm_content=request.utm_content,
        referrer=request.referrer,
        user_agent=request.user_agent,
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return {
        "session_id": new_session.session_id,
        "status": "created",
        "message": "Session tracked successfully",
    }


@router.post("/update-session-telegram", response_model=SessionResponseSchema)
async def update_session_telegram(
    request: UpdateSessionTelegramSchema, db: AsyncSession = Depends(get_db)
) -> dict:
    """Update session with Telegram user data.

    Args:
        request: Session ID and Telegram user data
        db: Database session

    Returns:
        Updated session confirmation

    Raises:
        HTTPException: If session not found
    """
    # Find session
    session = await db.scalar(
        select(WebSession).where(WebSession.session_id == request.session_id)
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "session_not_found",
                    "message": "Session not found",
                }
            },
        )

    # Update with Telegram data
    session.telegram_id = request.telegram_id  # type: ignore[assignment]
    session.telegram_username = request.telegram_username  # type: ignore[assignment]
    session.bot_started_at = datetime.utcnow()  # type: ignore[assignment]
    session.updated_at = datetime.utcnow()  # type: ignore[assignment]

    await db.commit()

    return {
        "session_id": session.session_id,
        "status": "updated",
        "message": "Telegram data added to session",
    }
