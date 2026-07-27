"""Shared Purchase projection context."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.domains.group.templates.shared_purchase.constants import PurchaseProfileDefinition
from app.domains.moments.models import MomentModel


@dataclass
class SharedPurchaseContext:
    moment: MomentModel
    profile: PurchaseProfileDefinition
    profile_badge: str
    stage_badge: str
    status_badge: str
    moment_name: str
    purchase_goal: str
    target_amount_minor: int
    currency_code: str
    is_active: bool
    expense_count: int
    expense_total_minor: int
    contribution_total_minor: int
    payment_total_minor: int
    contributor_count: int
    active_contributor_count: int = 0
    pending_contributor_count: int = 0
    inactive_contributor_count: int = 0
    vendor_count: int = 0
    poll_count: int = 0
    milestone_count: int = 0
    decision_count: int = 0
    ownership_count: int = 0
    memory_count: int = 0
    item_count: int = 0
    shortlisted_count: int = 0
    in_progress_count: int = 0
    pending_item_count: int = 0
    document_count: int = 0
    invoice_count: int = 0
    receipt_count: int = 0
    setup_payload: dict = field(default_factory=dict)
    activities: list[dict] = field(default_factory=list)
    contributions: list[dict] = field(default_factory=list)
    payments: list[dict] = field(default_factory=list)
    installments: list[dict] = field(default_factory=list)
    ownership_shares: list[dict] = field(default_factory=list)
    milestones: list[dict] = field(default_factory=list)
    decisions: list[dict] = field(default_factory=list)
    notes: list[dict] = field(default_factory=list)
    guests: list[dict] = field(default_factory=list)
    vendors: list[dict] = field(default_factory=list)
    polls: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    items: list[dict] = field(default_factory=list)
    primary_organizer: dict | None = None
    role_counts: list[dict] = field(default_factory=list)
    participant_avatars: list[str] = field(default_factory=list)

    @property
    def amount_remaining_minor(self) -> int:
        return max(0, self.target_amount_minor - self.contribution_total_minor)

    @property
    def contribution_progress_percent(self) -> float:
        if self.target_amount_minor <= 0:
            return 0.0
        return min(100.0, (self.contribution_total_minor / self.target_amount_minor) * 100.0)
