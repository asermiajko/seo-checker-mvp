"""Database models (SQLAlchemy)."""


from sqlalchemy import (
    DECIMAL,
    JSON,
    TIMESTAMP,
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class WebSession(Base):  # type: ignore[misc]
    """Web session for UTM tracking and attribution."""

    __tablename__ = "web_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    
    # UTM tracking
    utm_source = Column(String(255), nullable=True)
    utm_medium = Column(String(255), nullable=True)
    utm_campaign = Column(String(255), nullable=True)
    utm_term = Column(String(255), nullable=True)
    utm_content = Column(String(255), nullable=True)
    referrer = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Telegram user data (filled when user opens bot)
    telegram_id = Column(BigInteger, nullable=True, index=True)
    telegram_username = Column(String(255), nullable=True)
    bot_started_at = Column(TIMESTAMP, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    
    # Relationship to check requests
    check_requests = relationship("CheckRequest", back_populates="session")

    def __repr__(self) -> str:
        return (
            f"<WebSession(session_id={self.session_id}, "
            f"utm_source={self.utm_source}, telegram_id={self.telegram_id})>"
        )


class CheckRequest(Base):  # type: ignore[misc]
    """User-initiated SEO check request."""

    __tablename__ = "check_requests"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    site_url = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")
    session_id = Column(UUID(as_uuid=True), ForeignKey("web_sessions.session_id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    result = relationship(
        "CheckResult",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan",
    )
    session = relationship("WebSession", back_populates="check_requests")

    def __repr__(self) -> str:
        return f"<CheckRequest(id={self.id}, site_url={self.site_url}, status={self.status})>"


class CheckResult(Base):  # type: ignore[misc]
    """SEO check result with detailed report."""

    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True, index=True)
    check_request_id = Column(
        Integer, ForeignKey("check_requests.id", ondelete="CASCADE"), nullable=False
    )
    score: Column[float] = Column(DECIMAL(3, 1), nullable=False)
    problems_critical = Column(Integer, default=0)
    problems_important = Column(Integer, default=0)
    checks_ok = Column(Integer, default=0)
    report_data = Column(JSON, nullable=False)
    detailed_checks = Column(JSON, nullable=False)
    processing_time_sec = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())

    request = relationship("CheckRequest", back_populates="result")

    def __repr__(self) -> str:
        return (
            f"<CheckResult(id={self.id}, score={self.score}, "
            f"critical={self.problems_critical})>"
        )
