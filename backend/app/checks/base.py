"""Base classes for SEO checks."""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class CheckResult:
    """Result of a single SEO check."""

    id: str
    name: str
    status: Literal["ok", "partial", "problem", "error"]
    message: str
    severity: Optional[Literal["critical", "important", "enhancement"]] = None
    category: str = "technical"

    def __repr__(self) -> str:
        return f"<CheckResult(id={self.id}, status={self.status})>"
