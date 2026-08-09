"""GroupActivityEngine — canonical write path for group template actions."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group.activity.types import ActivityType, collection_for
from app.domains.group.projection_cache import invalidate_group_projections
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


def _title_for(activity_type: ActivityType, body: dict[str, Any]) -> str:
    mapping = {
        ActivityType.EXPENSE: str(body.get("description") or body.get("title") or "Expense"),
        ActivityType.BOOKING: str(body.get("title") or body.get("name") or "Booking"),
        ActivityType.PARTICIPANT: str(body.get("full_name") or body.get("name") or "Participant"),
        ActivityType.CONTRIBUTION: str(body.get("title") or "Contribution"),
        ActivityType.POLL: str(body.get("question") or "Poll"),
        ActivityType.TASK: str(body.get("title") or "Task"),
        ActivityType.MEMORY: str(body.get("title") or "Memory"),
        ActivityType.VENDOR: str(body.get("name") or body.get("vendor_name") or body.get("title") or "Vendor"),
        ActivityType.ATTENDANCE: str(body.get("label") or body.get("title") or "Attendance"),
        ActivityType.UPDATE: str(body.get("title") or body.get("message") or body.get("body") or "Update"),
        ActivityType.PLANNING_ITEM: str(body.get("title") or "Plan item"),
        ActivityType.PAYMENT: str(body.get("title") or "Payment"),
        ActivityType.INSTALLMENT: str(body.get("title") or "Installment"),
        ActivityType.OWNERSHIP_UPDATE: str(body.get("title") or "Ownership update"),
        ActivityType.DECISION: str(body.get("title") or body.get("question") or "Decision"),
        ActivityType.MILESTONE: str(body.get("title") or body.get("event_type") or "Milestone"),
        ActivityType.NOTE: str(body.get("title") or body.get("body") or "Note"),
        ActivityType.DOCUMENT_PLACEHOLDER: str(body.get("title") or "Document"),
        ActivityType.RENT: str(body.get("title") or "Rent"),
        ActivityType.UTILITY: str(body.get("title") or "Utility"),
        ActivityType.GROCERY: str(body.get("title") or "Grocery"),
        ActivityType.HOUSEHOLD_EXPENSE: str(body.get("description") or body.get("title") or "Household expense"),
        ActivityType.CHORE: str(body.get("title") or "Chore"),
        ActivityType.HOUSEHOLD_PURCHASE: str(body.get("title") or body.get("item_name") or "Household purchase"),
        ActivityType.MAINTENANCE: str(body.get("title") or "Maintenance"),
        ActivityType.SETTLEMENT_NOTE: str(body.get("title") or "Settlement note"),
        ActivityType.MEMBER_UPDATE: str(body.get("full_name") or body.get("name") or "Member"),
        ActivityType.HOME_MEMORY: str(body.get("title") or "Home memory"),
    }
    return mapping.get(activity_type, activity_type.value.replace("_", " ").title())


def _subtitle_for(activity_type: ActivityType, body: dict[str, Any]) -> str:
    if activity_type in {ActivityType.EXPENSE, ActivityType.HOUSEHOLD_EXPENSE, ActivityType.RENT, ActivityType.UTILITY, ActivityType.GROCERY}:
        minor = int(body.get("amount_minor") or 0)
        currency = str(body.get("currency_code") or "INR")
        return f"{currency} {minor / 100:.2f}"
    if activity_type in {ActivityType.CONTRIBUTION, ActivityType.PAYMENT}:
        minor = int(body.get("amount_minor") or 0)
        return f"{'Paid' if activity_type == ActivityType.PAYMENT else 'Contributed'} {minor / 100:.2f}"
    if activity_type in {ActivityType.MEMORY, ActivityType.HOME_MEMORY}:
        return str(body.get("note") or body.get("caption") or "Captured a moment")
    if activity_type in {ActivityType.PARTICIPANT, ActivityType.MEMBER_UPDATE}:
        return str(body.get("status") or "invited")
    return str(body.get("subtitle") or activity_type.value.replace("_", " ").title())


class GroupActivityEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)

    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    async def write(
        self,
        user_id: UUID,
        moment_id: UUID,
        activity_type: ActivityType,
        body: dict[str, Any],
        *,
        actor_name: str = "You",
    ) -> dict[str, Any]:
        from app.domains.group.expense_contract import resolve_group_default_currency
        from app.domains.quick_add_contract.normalize import normalize_payload

        moment = await self._require(user_id, moment_id)
        collection = collection_for(activity_type)
        normalized = normalize_payload(body or {})
        client_request_id = normalized.get("client_request_id") or (body or {}).get(
            "client_request_id"
        )
        if client_request_id:
            existing = store.find_by_client_request_id(
                moment, collection, str(client_request_id)
            )
            if existing is not None:
                return {**existing, "idempotent_replay": True}

        row_id = str(
            (body or {}).get("id")
            or normalized.get("id")
            or store.new_id()
        )
        created_at = store.now_iso()

        row: dict[str, Any] = {
            "id": row_id,
            "created_at": created_at,
            "deleted": False,
            **{k: v for k, v in normalized.items() if k != "id"},
        }
        row["id"] = row_id
        if client_request_id:
            row["client_request_id"] = str(client_request_id)
        if activity_type in {ActivityType.EXPENSE, ActivityType.HOUSEHOLD_EXPENSE}:
            payer = (
                normalized.get("paid_by_participant_id")
                or normalized.get("paid_by_user_id")
                or str(user_id)
            )
            row.setdefault("paid_by_user_id", payer)
            row.setdefault(
                "currency_code",
                resolve_group_default_currency(normalized),
            )
            row.setdefault("split_type", str(normalized.get("split_style") or "equal").lower())
            row.setdefault("expense_date", created_at)
            if "amount_minor" not in row and "amount_major" in (body or {}):
                row["amount_minor"] = store.to_minor((body or {}).get("amount_major"))
        if activity_type in {ActivityType.CONTRIBUTION, ActivityType.PAYMENT, ActivityType.INSTALLMENT}:
            row.setdefault("contributor_user_id", str(user_id))
            row.setdefault(
                "currency_code",
                resolve_group_default_currency(normalized),
            )
        if activity_type in {ActivityType.PARTICIPANT, ActivityType.MEMBER_UPDATE}:
            row.setdefault("status", "invited")
            row.setdefault("relationship_type", "friend")
            if normalized.get("title") and not row.get("name"):
                row.setdefault("name", normalized["title"])
        if activity_type in {ActivityType.MEMORY, ActivityType.HOME_MEMORY}:
            row.setdefault("created_by_user_id", str(user_id))
            row.setdefault("created_by_name", actor_name)

        store.append_item(moment, collection, row)
        self._append_timeline(
            moment,
            activity_type=activity_type,
            row_id=row_id,
            title=_title_for(activity_type, body),
            subtitle=_subtitle_for(activity_type, body),
            occurred_at=created_at,
        )
        await self.session.flush()
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=moment.moment_type or "SHARED_EXPERIENCE",
            reason=f"activity:{activity_type.value}",
            session=self.session,
            moment=moment,
        )
        return row

    async def patch_activity(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: str,
        patch: dict[str, Any],
    ) -> dict[str, Any]:
        moment = await self._require(user_id, moment_id)
        updated = self._patch_timeline_item(moment, event_id, patch)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        await self.session.flush()
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=moment.moment_type or "SHARED_EXPERIENCE",
            reason="activity:patch",
            session=self.session,
            moment=moment,
        )
        return updated

    async def delete_activity(self, user_id: UUID, moment_id: UUID, event_id: str) -> dict[str, Any]:
        moment = await self._require(user_id, moment_id)
        updated = self._patch_timeline_item(moment, event_id, {"deleted": True, "deleted_at": store.now_iso()})
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        ref_id = updated.get("ref_id")
        activity_type = updated.get("activity_type")
        if ref_id and activity_type:
            try:
                collection = collection_for(ActivityType(activity_type))
                self._soft_delete_collection_item(moment, collection, str(ref_id))
            except ValueError:
                pass
        await self.session.flush()
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=moment.moment_type or "SHARED_EXPERIENCE",
            reason="activity:delete",
            session=self.session,
            moment=moment,
        )
        return {"status": "deleted", "event_id": event_id}

    @staticmethod
    def _find_timeline_item(moment: MomentModel, event_id: str) -> dict[str, Any] | None:
        """Match by timeline id, or by ref_id (entity id) for clients that have the source row id."""
        needle = str(event_id)
        for item in store.list_activities(moment):
            if item.get("deleted"):
                continue
            if str(item.get("id") or "") == needle:
                return item
            if str(item.get("ref_id") or "") == needle:
                return item
        return None

    @staticmethod
    def _append_timeline(
        moment: MomentModel,
        *,
        activity_type: ActivityType,
        row_id: str,
        title: str,
        subtitle: str,
        occurred_at: str,
    ) -> None:
        store.append_activity(
            moment,
            {
                "id": store.new_id(),
                "activity_type": activity_type.value,
                "ref_id": row_id,
                "title": title,
                "subtitle": subtitle,
                "icon": activity_type.value.lower(),
                "occurred_at": occurred_at,
                "deleted": False,
            },
        )

    @staticmethod
    def _patch_timeline_item(moment: MomentModel, event_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
        state = store.read_state(moment)
        activities = state["runtime"].get("activities", [])
        needle = str(event_id)
        for item in activities:
            if item.get("deleted"):
                continue
            if str(item.get("id") or "") != needle and str(item.get("ref_id") or "") != needle:
                continue
            item.update(patch)
            store.write_state(moment, state)
            return item
        return None

    @staticmethod
    def _soft_delete_collection_item(moment: MomentModel, collection: str, ref_id: str) -> None:
        state = store.read_state(moment)
        items = state["runtime"].get(collection, [])
        for item in items:
            if str(item.get("id")) == ref_id:
                item["deleted"] = True
                item["deleted_at"] = store.now_iso()
                break
        store.write_state(moment, state)

    async def list_timeline(self, user_id: UUID, moment_id: UUID) -> list[dict[str, Any]]:
        moment = await self._require(user_id, moment_id)
        return [a for a in store.list_activities(moment) if not a.get("deleted")]
