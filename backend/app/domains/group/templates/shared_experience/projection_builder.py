"""Build Shared Experience projection context from moment_store."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group import shared_catalog as cat
from app.domains.group.experience_types.registry import get_experience_type
from app.domains.group.templates.shared_experience.context import SharedExperienceContext
from app.domains.group.templates.shared_experience.projection_helpers import (
    booking_is_cancelled,
    booking_is_confirmed,
    days_remaining,
)
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


def _member_status_counts(members: list[dict]) -> tuple[int, int, int]:
    active = pending = inactive = 0
    for row in members:
        if row.get("deleted"):
            continue
        status = str(row.get("status") or "ACTIVE").upper()
        if status in {"ACTIVE", "ACCEPTED"}:
            active += 1
        elif status in {"INVITED", "PENDING"}:
            pending += 1
        else:
            inactive += 1
    return active, pending, inactive


def _primary_organizer(members: list[dict]) -> dict | None:
    for row in members:
        if row.get("deleted"):
            continue
        role = str(row.get("role_code") or "").upper()
        if role in {"ORGANIZER", "LEAD_ORGANIZER", "OWNER"}:
            return {
                "user_id": str(row.get("user_id") or row.get("id") or ""),
                "display_name": str(row.get("display_name") or "Organizer"),
                "role_label": "LEAD ORGANIZER",
                "avatar_url": row.get("avatar_url"),
                "is_primary": True,
            }
    for row in members:
        if not row.get("deleted"):
            return {
                "user_id": str(row.get("user_id") or row.get("id") or ""),
                "display_name": str(row.get("display_name") or "Organizer"),
                "role_label": "ORGANIZER",
                "avatar_url": row.get("avatar_url"),
                "is_primary": True,
            }
    return None


def _role_counts(members: list[dict], guests: list[dict]) -> list[dict]:
    organizers = sum(
        1
        for m in members
        if not m.get("deleted")
        and str(m.get("role_code") or "").upper() in {"ORGANIZER", "LEAD_ORGANIZER", "OWNER"}
    )
    attendees = max(0, len([g for g in guests if not g.get("deleted")]) - organizers)
    if organizers:
        return [
            {"label": "Organizers", "count": organizers},
            {"label": "Attendees", "count": max(attendees, len(guests) - organizers)},
        ]
    return [{"label": "Participants", "count": len(guests)}]


class SharedExperienceProjectionBuilder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)

    async def build(self, user_id: UUID, moment_id: UUID) -> SharedExperienceContext:
        from app.domains.group.access import require_group_moment_access

        moment = await require_group_moment_access(self.session, user_id, moment_id)
        return self.build_from_moment(moment)

    @staticmethod
    def build_from_moment(moment: MomentModel) -> SharedExperienceContext:
        state = store.read_state(moment)
        payload = state.get("payload") or {}
        code = store.profile_code(moment)
        category = moment.moment_type or cat.EXPERIENCE
        profile_badge = cat.profile_name(category, code) if code else "Experience"
        exp_type = get_experience_type(code)
        is_active = (moment.status or "DRAFT") == "ACTIVE"
        status_badge = "Active" if is_active else "Draft"
        stage_badge = "Planning" if is_active else "Setup"
        if str(moment.status or "").upper() == "COMPLETED":
            stage_badge = "Completed"
        elif is_active and store.plan_count(moment) > 0:
            stage_badge = "Planning"

        exp_count, exp_total = store.expense_summary(moment)
        members = store.list_accepted_members(moment)
        all_members = store.list_items(moment, "members")
        guests = store.guest_summaries(moment)
        bookings = [
            b
            for b in store.list_items(moment, "bookings")
            if not b.get("deleted") and not booking_is_cancelled(b)
        ]
        activities = [
            a for a in store.list_activities(moment) if not a.get("deleted")
        ]
        # Timeline BOOKING rows are the source of truth for Recent Activity; if the
        # bookings collection is empty/out of sync, still count those toward KPIs.
        timeline_bookings = [
            a
            for a in activities
            if str(a.get("activity_type") or "").upper() == "BOOKING"
        ]
        booking_ids = {str(b.get("id") or "") for b in bookings if b.get("id")}
        orphan_timeline_bookings = [
            a
            for a in timeline_bookings
            if str(a.get("ref_id") or a.get("id") or "") not in booking_ids
        ]
        booking_count = len(bookings) + len(orphan_timeline_bookings)
        polls = [p for p in store.list_items(moment, "polls") if not p.get("deleted")]
        plans = [p for p in store.list_items(moment, "plans") if not p.get("deleted")]
        memories = [m for m in store.list_items(moment, "memories") if not m.get("deleted")]
        documents = [d for d in store.list_items(moment, "documents") if not d.get("deleted")]
        vendors = [v for v in store.list_items(moment, "vendors") if not v.get("deleted")]

        active_m, pending_m, inactive_m = _member_status_counts(all_members or members)
        budget_minor = store.to_minor(payload.get("target_amount_major") or payload.get("estimated_budget"))
        if not budget_minor:
            for bp in store.list_items(moment, "budget_plans"):
                if not bp.get("deleted"):
                    budget_minor = max(budget_minor, int(bp.get("amount_minor") or 0))

        currency = str(payload.get("currency_code") or "INR")
        confirmed_bookings = sum(1 for b in bookings if booking_is_confirmed(b))
        # Timeline-only bookings have no status → treat as countable (hero "Bookings").
        if orphan_timeline_bookings and confirmed_bookings == 0:
            confirmed_bookings = booking_count
        booking_spend = sum(int(b.get("amount_minor") or 0) for b in bookings)
        for a in orphan_timeline_bookings:
            booking_spend += int(a.get("amount_minor") or 0)
        # Hero "Spent" should include booking amounts (Quick Add bookings carry money).
        spent_minor = exp_total + booking_spend
        open_polls = sum(
            1 for p in polls if str(p.get("status", "open")).lower() not in {"closed", "resolved"}
        )
        contributions = store.contribution_summary(moment)
        avatars = [
            str(m.get("avatar_url"))
            for m in (all_members or members)
            if m.get("avatar_url") and not m.get("deleted")
        ][:5]

        return SharedExperienceContext(
            moment=moment,
            experience_type=exp_type,
            profile_badge=profile_badge,
            stage_badge=stage_badge,
            status_badge=status_badge,
            moment_name=moment.title or "Your Experience",
            is_active=is_active,
            currency_code=currency,
            setup_payload=payload,
            expense_count=exp_count,
            expense_total_minor=spent_minor,
            contribution_total_minor=contributions,
            guest_count=len(guests),
            member_count=len(all_members) or len(members),
            active_member_count=active_m or len(members),
            pending_member_count=pending_m,
            inactive_member_count=inactive_m,
            memory_count=len(memories),
            plan_count=len(plans),
            booking_count=booking_count,
            confirmed_booking_count=confirmed_bookings,
            open_poll_count=open_polls,
            vendor_count=len(vendors),
            document_count=len(documents),
            budget_minor=budget_minor,
            corpus_balance_minor=max(0, contributions - spent_minor),
            days_remaining=days_remaining(payload.get("end_date")),
            activities=activities,
            guests=guests,
            members=all_members or members,
            bookings=bookings,
            polls=polls,
            plans=plans,
            memories=memories,
            documents=documents,
            vendors=vendors,
            updates=[u for u in store.list_items(moment, "updates") if not u.get("deleted")],
            primary_organizer=_primary_organizer(all_members or members),
            role_counts=_role_counts(all_members or members, guests),
            participant_avatars=avatars,
        )
