"""Shared Living projection context."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.domains.group.templates.shared_living.constants import LivingProfileDefinition
from app.domains.moments.models import MomentModel


@dataclass
class SharedLivingContext:
    moment: MomentModel
    profile: LivingProfileDefinition
    profile_badge: str
    stage_badge: str
    status_badge: str
    moment_name: str
    home_description: str
    currency_code: str
    is_active: bool
    resident_count: int
    expense_count: int
    expense_total_minor: int
    contribution_total_minor: int
    task_count: int
    rules_count: int
    assets_count: int
    maintenance_count: int
    poll_count: int
    memory_count: int
    update_count: int
    active_resident_count: int = 0
    pending_resident_count: int = 0
    inactive_resident_count: int = 0
    setup_payload: dict = field(default_factory=dict)
    activities: list[dict] = field(default_factory=list)
    residents: list[dict] = field(default_factory=list)
    expenses: list[dict] = field(default_factory=list)
    contributions: list[dict] = field(default_factory=list)
    chores: list[dict] = field(default_factory=list)
    rules: list[dict] = field(default_factory=list)
    assets: list[dict] = field(default_factory=list)
    maintenance: list[dict] = field(default_factory=list)
    updates: list[dict] = field(default_factory=list)
    polls: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    primary_organizer: dict | None = None
    role_counts: list[dict] = field(default_factory=list)
    participant_avatars: list[str] = field(default_factory=list)
