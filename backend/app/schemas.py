"""Pydantic schemas for API requests and responses."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class CheckRequestSchema(BaseModel):
    """Request schema for POST /api/check."""

    site_url: str = Field(..., min_length=1, max_length=500)
    telegram_id: int = Field(..., gt=0)

    @field_validator("site_url")
    @classmethod
    def validate_site_url(cls, v: str) -> str:
        """Validate site URL."""
        # Must start with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("site_url must start with http:// or https://")

        # Block localhost and private IPs (SSRF protection)
        lower_url = v.lower()
        blocked = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "10.",
            "192.168.",
            "172.16.",
        ]
        for blocked_host in blocked:
            if blocked_host in lower_url:
                raise ValueError(f"site_url cannot contain {blocked_host}")

        return v


class CategorySchema(BaseModel):
    """Category group in report."""

    name: str
    score: int
    total: int
    checks: list[str]


class PrioritySchema(BaseModel):
    """Priority issue in report."""

    severity: Literal["critical", "important", "enhancement"]
    title: str
    message: str
    check_id: str


class DetailedCheckSchema(BaseModel):
    """Detailed check result."""

    id: str
    name: str
    status: Literal["ok", "partial", "problem", "error"]
    message: str
    category: Literal["technical", "content", "structure", "seo", "social"]
    severity: Optional[Literal["critical", "important", "enhancement"]] = None


class MetadataSchema(BaseModel):
    """Check metadata."""

    checked_at: str
    processing_time_sec: int
    checks_total: int
    checks_completed: int
    checks_failed: int


class CheckResponseSchema(BaseModel):
    """Response schema for POST /api/check."""

    score: float = Field(..., ge=0.0, le=10.0)
    problems_critical: int
    problems_important: int
    checks_ok: int
    categories: list[CategorySchema]
    top_priorities: list[PrioritySchema]
    detailed_checks: list[DetailedCheckSchema]
    metadata: MetadataSchema


class ErrorResponseSchema(BaseModel):
    """Error response schema."""

    error: dict[str, Any]
