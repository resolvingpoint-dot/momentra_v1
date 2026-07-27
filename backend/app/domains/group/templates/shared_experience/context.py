"""Shared Experience projection context."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.domains.group.experience_types.registry import ExperienceTypeDefinition
from app.domains.moments.models import MomentModel


@dataclass
class SharedExperienceContext:
    moment: MomentModel
    experience_type: ExperienceTypeDefinition
    profile_badge: str
    stage_badge: str
    status_badge: str
    moment_name: str
    is_active: bool
    currency_code: str = "INR"
    setup_payload: dict = field(default_factory=dict)
    expense_count: int = 0
    expense_total_minor: int = 0
    contribution_total_minor: int = 0
    guest_count: int = 0
    member_count: int = 0
    active_member_count: int = 0
    pending_member_count: int = 0
    inactive_member_count: int = 0
    memory_count: int = 0
    plan_count: int = 0
    booking_count: int = 0
    confirmed_booking_count: int = 0
    open_poll_count: int = 0
    vendor_count: int = 0
    document_count: int = 0
    budget_minor: int = 0
    corpus_balance_minor: int = 0
    days_remaining: int | None = None
    activities: list[dict] = field(default_factory=list)
    guests: list[dict] = field(default_factory=list)
    members: list[dict] = field(default_factory=list)
    bookings: list[dict] = field(default_factory=list)
    polls: list[dict] = field(default_factory=list)
    plans: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    documents: list[dict] = field(default_factory=list)
    vendors: list[dict] = field(default_factory=list)
    updates: list[dict] = field(default_factory=list)
    primary_organizer: dict | None = None
    role_counts: list[dict] = field(default_factory=list)
    participant_avatars: list[str] = field(default_factory=list)
