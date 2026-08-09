"""Build Shared Living projection context from moment_store."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group import shared_catalog as cat
from app.domains.group.templates.shared_living.constants import get_living_profile
from app.domains.group.templates.shared_living.context import SharedLivingContext
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


def _active_items(items: list[dict]) -> list[dict]:
    return [i for i in items if not i.get("deleted")]


def _sum_minor(items: list[dict], key: str = "amount_minor") -> int:
    total = 0
    for row in items:
        try:
            total += int(row.get(key) or 0)
        except (ValueError, TypeError):
            pass
    return total


def _resident_items(moment: MomentModel) -> list[dict]:
    return _active_items(store.list_items(moment, "residents")) + _active_items(store.list_items(moment, "guests"))


def _resident_status_counts(residents: list[dict]) -> tuple[int, int, int]:
    active = pending = inactive = 0
    for row in residents:
        status = str(row.get("status") or "invited").lower()
        if status in {"active", "joined", "confirmed"}:
            active += 1
        elif status in {"pending", "invited", "maybe"}:
            pending += 1
        else:
            inactive += 1
    if active + pending + inactive == 0 and residents:
        active = len(residents)
    return active, pending, inactive


def _primary_organizer(residents: list[dict]) -> dict | None:
    if not residents:
        return None
    primary = next(
        (
            r
            for r in residents
            if str(r.get("role") or r.get("assigned_role") or r.get("resident_role") or "").lower()
            in {"owner", "primary", "primary owner", "landlord"}
        ),
        residents[0],
    )
    return {
        "user_id": str(primary.get("user_id") or primary.get("id") or ""),
        "display_name": str(
            primary.get("display_name") or primary.get("full_name") or primary.get("name") or "Resident"
        ),
        "role_label": str(
            primary.get("assigned_role") or primary.get("resident_role") or primary.get("role") or "Primary"
        ),
        "avatar_url": primary.get("avatar_url"),
    }


def _role_counts(residents: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for r in residents:
        role = str(r.get("assigned_role") or r.get("resident_role") or r.get("role") or "Resident")
        counts[role] = counts.get(role, 0) + 1
    if not counts:
        return [{"label": "Residents", "count": 0}]
    return [{"label": role, "count": count} for role, count in counts.items()]


class SharedLivingProjectionBuilder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)

    async def build(self, user_id: UUID, moment_id: UUID) -> SharedLivingContext:
        from app.domains.group.access import require_group_moment_access

        moment = await require_group_moment_access(self.session, user_id, moment_id)
        return self.build_from_moment(moment)

    @staticmethod
    def build_from_moment(moment: MomentModel) -> SharedLivingContext:
        code = store.profile_code(moment)
        category = moment.moment_type or cat.LIVING
        profile = get_living_profile(code)
        profile_badge = cat.profile_name(category, code) if code else profile.name
        is_active = (moment.status or "DRAFT") == "ACTIVE"
        state = store.read_state(moment)
        payload = state.get("payload") or {}
        currency = str(payload.get("currency_code") or "INR")
        home_description = str(payload.get("description") or payload.get("home_description") or "")
        expenses = _active_items(store.list_items(moment, "expenses"))
        contributions = _active_items(store.list_items(moment, "contributions"))
        chores = _active_items(store.list_items(moment, "chores")) + _active_items(store.list_items(moment, "tasks"))
        rules = _active_items(store.list_items(moment, "notes"))
        assets = _active_items(store.list_items(moment, "household_purchases"))
        maintenance = _active_items(store.list_items(moment, "maintenance"))
        updates = _active_items(store.list_items(moment, "updates"))
        polls = _active_items(store.list_items(moment, "polls"))
        memories = _active_items(store.list_items(moment, "memories"))
        residents = _resident_items(moment)
        active_r, pending_r, inactive_r = _resident_status_counts(residents)
        avatars = [str(r.get("avatar_url")) for r in residents if r.get("avatar_url")][:8]
        expected_residents = payload.get("expected_residents") if isinstance(payload, dict) else None
        try:
            expected_resident_count = int(expected_residents) if expected_residents is not None else None
        except (TypeError, ValueError):
            expected_resident_count = None
        return SharedLivingContext(
            moment=moment,
            profile=profile,
            profile_badge=profile_badge,
            stage_badge="Live" if is_active else "Setup",
            status_badge="Active" if is_active else "Draft",
            moment_name=moment.title or "Your Home",
            home_description=home_description,
            currency_code=currency,
            is_active=is_active,
            resident_count=len(residents),
            expected_resident_count=expected_resident_count,
            expense_count=len(expenses),
            expense_total_minor=_sum_minor(expenses),
            contribution_total_minor=_sum_minor(contributions),
            task_count=len(chores),
            rules_count=len(rules),
            assets_count=len(assets),
            maintenance_count=len(maintenance),
            poll_count=len(polls),
            memory_count=len(memories) or store.memory_count(moment),
            update_count=len(updates),
            active_resident_count=active_r,
            pending_resident_count=pending_r,
            inactive_resident_count=inactive_r,
            setup_payload=payload if isinstance(payload, dict) else {},
            activities=[a for a in store.list_activities(moment) if not a.get("deleted")],
            residents=residents,
            expenses=expenses,
            contributions=contributions,
            chores=chores,
            rules=rules,
            assets=assets,
            maintenance=maintenance,
            updates=updates,
            polls=polls,
            memories=memories,
            primary_organizer=_primary_organizer(residents),
            role_counts=_role_counts(residents),
            participant_avatars=avatars,
        )
