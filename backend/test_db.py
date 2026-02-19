#!/usr/bin/env python3
"""Test database connection and create tables."""

import asyncio

from sqlalchemy import text

from app.database import engine, init_db, settings
from app.models import CheckRequest, CheckResult


async def test_connection() -> None:
    """Test database connection."""
    print("🔍 Testing database connection...")
    print(f"   Database URL: {settings.database_url[:50]}...")

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")

        print("\n📦 Creating tables...")
        await init_db()
        print("✅ Tables created successfully")

        print("\n📊 Database schema:")
        print(f"   - {CheckRequest.__tablename__} ({len(CheckRequest.__table__.columns)} columns)")
        print(f"   - {CheckResult.__tablename__} ({len(CheckResult.__table__.columns)} columns)")

    except Exception as e:
        print(f"❌ Database error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())
