"""Team Operations projection context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.domains.business.templates.base import BusinessProjectionContext

if TYPE_CHECKING:
    from app.domains.business.templates.team_operations.projector import TeamOpsProjectionBundle


@dataclass
class TeamOpsContext(BusinessProjectionContext):
    team_name: str = ""
    operating_currency: str = "INR"
    monthly_budget_minor: int | None = None
    open_issues: int = 0
    pending_approvals: int = 0
    recognition_count: int = 0
    meeting_count: int = 0
    escalation_count: int = 0
    participation_count: int = 0
    member_names: list[str] = field(default_factory=list)
    projection: "TeamOpsProjectionBundle | None" = None
