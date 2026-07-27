"""Base projection context for Business templates."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from app.domains.business.models import BusinessMoments


@dataclass
class BusinessProjectionContext:
    """Common fields every business template context carries."""
    moment: BusinessMoments
    moment_id: UUID
    moment_type: str
    moment_name: str
    status: str
    is_active: bool
    member_count: int = 0
    activity_count: int = 0
    activities: list[dict] = field(default_factory=list)
