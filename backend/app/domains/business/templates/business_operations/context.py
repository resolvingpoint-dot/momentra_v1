"""Business Operations projection context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from app.domains.business.templates.base import BusinessProjectionContext

if TYPE_CHECKING:
    from app.domains.business.templates.business_operations.projector import OpsProjectionBundle


@dataclass
class OpsContext(BusinessProjectionContext):
    operating_currency: str = "INR"
    operations_name: str = ""
    operations_scope: str | None = None
    operating_model: str | None = None
    owner_name: str | None = None
    last_updated: str | None = None
    monitoring_level: str | None = None
    monthly_budget_minor: int = 0
    total_spend_minor: int = 0
    total_budget_minor: int = 0
    remaining_minor: int = 0
    budget_usage_pct: float = 0.0
    unallocated_minor: int = 0
    allocations: list[dict[str, Any]] = field(default_factory=list)
    over_budget_allocations: list[dict[str, Any]] = field(default_factory=list)
    vendor_count: int = 0
    critical_vendor_count: int = 0
    # casefold(vendor name) → outstanding spend due_minor for Moments Vendors cards
    vendor_due_by_name: dict[str, int] = field(default_factory=dict)
    pending_approvals: int = 0
    overdue_approval_count: int = 0
    approved_recently: int = 0
    rejected_recently: int = 0
    amount_awaiting_minor: int | None = None
    open_issue_count: int = 0
    critical_issue_count: int = 0
    overdue_issue_count: int = 0
    unassigned_issue_count: int = 0
    resolved_recently: int = 0
    improvement_count: int = 0
    planned_improvement_count: int = 0
    in_progress_improvement_count: int = 0
    completed_improvement_count: int = 0
    overdue_improvement_count: int = 0
    activated_at: str | None = None
    projection: OpsProjectionBundle | None = None
    stage_timings_ms: dict[str, float] = field(default_factory=dict)
    member_picker: list[dict[str, Any]] = field(default_factory=list)
