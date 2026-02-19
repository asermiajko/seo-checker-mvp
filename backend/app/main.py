"""Main FastAPI application entry point."""

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routes.check import router as check_router
from app.routes.session import router as session_router

app = FastAPI(
    title="SEO Checker API", description="API for checking website SEO health", version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(check_router)
app.include_router(session_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - health check."""
    return {"message": "SEO Checker API is running", "version": "1.0.0"}


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Health check endpoint with database status."""
    # Check database connection
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": "1.0.0",
        "checks": {"database": db_status},
    }
