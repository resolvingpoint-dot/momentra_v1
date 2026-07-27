"""Build Shared Purchase projection context from moment_store."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group import shared_catalog as cat
from app.domains.group.templates.shared_purchase.constants import get_purchase_profile
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext
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


def _contributor_status_counts(guests: list[dict]) -> tuple[int, int, int]:
    active = pending = inactive = 0
    for g in guests:
        status = str(g.get("status") or g.get("invite_status") or "active").lower()
        if status in {"active", "paid", "joined", "confirmed"}:
            active += 1
        elif status in {"invited", "pending", "draft"}:
            pending += 1
        else:
            inactive += 1
    if active + pending + inactive == 0 and guests:
        active = len(guests)
    return active, pending, inactive


def _item_status_counts(items: list[dict]) -> tuple[int, int, int]:
    shortlisted = in_progress = pending = 0
    for item in items:
        status = str(item.get("status") or "proposed").lower()
        if status in {"shortlisted", "selected", "proposed"}:
            shortlisted += 1
        elif status in {"in_progress", "purchasing", "ordered"}:
            in_progress += 1
        elif status in {"pending", "waiting"}:
            pending += 1
        else:
            pending += 1
    return shortlisted, in_progress, pending


def _primary_organizer(guests: list[dict]) -> dict | None:
    if not guests:
        return None
    primary = next(
        (g for g in guests if str(g.get("role") or g.get("assigned_role") or "").lower() in {"owner", "primary", "primary owner"}),
        guests[0],
    )
    return {
        "user_id": str(primary.get("user_id") or primary.get("id") or ""),
        "display_name": str(primary.get("display_name") or primary.get("full_name") or "Owner"),
        "role_label": str(primary.get("assigned_role") or primary.get("role") or "Primary Owner"),
        "avatar_url": primary.get("avatar_url"),
    }


def _role_counts(guests: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for g in guests:
        role = str(g.get("assigned_role") or g.get("role") or "Contributor")
        counts[role] = counts.get(role, 0) + 1
    if not counts:
        return [{"label": "Contributors", "count": 0}]
    return [{"label": role, "count": count} for role, count in counts.items()]


class SharedPurchaseProjectionBuilder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)

    async def build(self, user_id: UUID, moment_id: UUID) -> SharedPurchaseContext:
        from app.domains.group.access import require_group_moment_access

        moment = await require_group_moment_access(self.session, user_id, moment_id)
        return self.build_from_moment(moment)

    @staticmethod
    def build_from_moment(moment: MomentModel) -> SharedPurchaseContext:
        code = store.profile_code(moment)
        category = moment.moment_type or cat.PURCHASE
        profile = get_purchase_profile(code)
        profile_badge = cat.profile_name(category, code) if code else profile.name
        is_active = (moment.status or "DRAFT") == "ACTIVE"
        state = store.read_state(moment)
        payload = state.get("payload") or {}
        target_minor = int(payload.get("target_amount_minor") or store.to_minor(payload.get("target_amount_major")) or 0)
        currency = str(payload.get("currency_code") or "INR")
        purchase_goal = str(payload.get("description") or payload.get("item_or_goal") or "")
        expenses = _active_items(store.list_items(moment, "expenses"))
        contributions = _active_items(store.list_items(moment, "contributions"))
        payments = _active_items(store.list_items(moment, "payments"))
        installments = _active_items(store.list_items(moment, "installments"))
        ownership = _active_items(store.list_items(moment, "ownership_shares"))
        milestones = _active_items(store.list_items(moment, "milestones"))
        decisions = _active_items(store.list_items(moment, "decisions"))
        notes = _active_items(store.list_items(moment, "notes"))
        guests = _active_items(store.list_items(moment, "guests"))
        vendors = _active_items(store.list_items(moment, "vendors"))
        polls = _active_items(store.list_items(moment, "polls"))
        memories = _active_items(store.list_items(moment, "memories"))
        items = _active_items(store.list_items(moment, "purchase_items") or store.list_items(moment, "items"))
        documents = _active_items(store.list_items(moment, "documents"))
        active_c, pending_c, inactive_c = _contributor_status_counts(guests)
        shortlisted, in_progress, pending_items = _item_status_counts(items) if items else (0, 0, 0)
        if not items and milestones:
            shortlisted = len([m for m in milestones if str(m.get("status", "")).lower() in {"proposed", "shortlisted"}])
            in_progress = len([m for m in milestones if str(m.get("status", "")).lower() in {"in_progress", "active"}])
            pending_items = max(0, len(milestones) - shortlisted - in_progress)
        invoices = [d for d in documents if "invoice" in str(d.get("purpose") or d.get("type") or "").lower()]
        receipts = [d for d in documents if "receipt" in str(d.get("purpose") or d.get("type") or "").lower()]
        avatars = [str(g.get("avatar_url")) for g in guests if g.get("avatar_url")][:8]
        return SharedPurchaseContext(
            moment=moment,
            profile=profile,
            profile_badge=profile_badge,
            stage_badge="Funding" if is_active and target_minor and _sum_minor(contributions) < target_minor else ("Live" if is_active else "Setup"),
            status_badge="Active" if is_active else "Draft",
            moment_name=moment.title or "Your Purchase",
            purchase_goal=purchase_goal,
            target_amount_minor=target_minor,
            currency_code=currency,
            is_active=is_active,
            expense_count=len(expenses),
            expense_total_minor=_sum_minor(expenses),
            contribution_total_minor=_sum_minor(contributions),
            payment_total_minor=_sum_minor(payments),
            contributor_count=len(guests),
            active_contributor_count=active_c,
            pending_contributor_count=pending_c,
            inactive_contributor_count=inactive_c,
            vendor_count=len(vendors),
            poll_count=len(polls),
            milestone_count=len(milestones),
            decision_count=len(decisions),
            ownership_count=len(ownership),
            memory_count=len(memories) or store.memory_count(moment),
            item_count=len(items) or len(milestones),
            shortlisted_count=shortlisted,
            in_progress_count=in_progress,
            pending_item_count=pending_items,
            document_count=len(documents),
            invoice_count=len(invoices),
            receipt_count=len(receipts),
            setup_payload=payload if isinstance(payload, dict) else {},
            activities=[a for a in store.list_activities(moment) if not a.get("deleted")],
            contributions=contributions,
            payments=payments,
            installments=installments,
            ownership_shares=ownership,
            milestones=milestones,
            decisions=decisions,
            notes=notes,
            guests=guests,
            vendors=vendors,
            polls=polls,
            memories=memories,
            items=items,
            primary_organizer=_primary_organizer(guests),
            role_counts=_role_counts(guests),
            participant_avatars=avatars,
        )
