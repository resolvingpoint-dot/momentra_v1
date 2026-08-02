"""BusinessActivityEngine — canonical write path for Business activity actions.

Sequence:
1. Membership + capability check
2. Validate action_type vs ACTION_REGISTRY
3. Insert business_activity_events (idempotent on client_request_id)
4. Dispatch typed handler → specialty row with event_id
5. Audit row
6. invalidate_business_projections
7. Return ActivityDTO
"""
from __future__ import annotations

import importlib
import logging
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.edit_schema import filter_patch
from app.domains.business.activity.registry import ACTION_REGISTRY
from app.domains.business.activity.repository import (
    find_by_client_request_id,
    get_event,
    insert_audit,
    insert_event,
    list_events,
    patch_event,
    soft_void_event,
)
from app.domains.business.activity.schemas import ActivityDTO, ActivityListResponse
from app.domains.business.activity.types import ActionType, moment_type_for_action
from app.domains.business.models import BusinessMomentMembers, BusinessMoments
from app.domains.business.permissions import (
    can_create_activity,
    can_delete_activity,
    can_edit_activity,
    get_active_member,
    member_may_delete,
    member_may_edit,
    require_moment_read_access,
)

logger = logging.getLogger(__name__)


def _auth_flags(
    event,
    *,
    viewer_id: UUID,
    member: BusinessMomentMembers | None,
) -> tuple[bool, bool, list[str]]:
    """Server-owned edit/delete flags from ACTION_REGISTRY + membership."""
    try:
        at = ActionType(event.action_type)
        meta = ACTION_REGISTRY.get(at, {})
    except ValueError:
        meta = {}

    registry_editable = bool(meta.get("editable", False))
    registry_deletable = bool(meta.get("deletable", False))

    if member is not None:
        may_edit = member_may_edit(member, viewer_id, created_by=event.created_by)
        may_delete = member_may_delete(member, viewer_id, created_by=event.created_by)
    else:
        # Owner-only read path (no membership row) — treat as full capability.
        may_edit = True
        may_delete = True

    is_editable = registry_editable and may_edit and not bool(event.is_voided)
    is_deletable = registry_deletable and may_delete and not bool(event.is_voided)
    supported: list[str] = []
    if is_editable:
        supported.append("edit")
    if is_deletable:
        supported.append("delete")
    return is_editable, is_deletable, supported


def _to_dto(
    event,
    *,
    viewer_id: UUID,
    member: BusinessMomentMembers | None = None,
    typed_row_id: UUID | None = None,
    replay: bool = False,
) -> dict:
    is_editable, is_deletable, supported_actions = _auth_flags(
        event, viewer_id=viewer_id, member=member
    )
    return ActivityDTO(
        event_id=event.event_id,
        business_moment_id=event.business_moment_id,
        user_id=event.user_id,
        moment_type_code=event.moment_type_code,
        action_type=event.action_type,
        title=event.title,
        subtitle=event.subtitle,
        occurred_at=event.occurred_at,
        created_by=event.created_by,
        source=event.source,
        payload=event.payload or {},
        client_request_id=event.client_request_id,
        is_voided=event.is_voided,
        typed_row_id=typed_row_id,
        idempotent_replay=replay,
        is_editable=is_editable,
        is_deletable=is_deletable,
        supported_actions=supported_actions,
    ).model_dump(mode="json")


class BusinessActivityEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _require_moment(self, moment_id: UUID) -> BusinessMoments:
        result = await self.session.execute(
            select(BusinessMoments).where(BusinessMoments.moment_id == moment_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business moment not found")
        return row

    async def create(
        self,
        user_id: UUID,
        moment_id: UUID,
        action_type: str,
        title: str,
        *,
        subtitle: str | None = None,
        payload: dict[str, Any] | None = None,
        client_request_id: str | None = None,
        source: str = "quick_add",
        actor_name: str = "You",
    ) -> dict:
        try:
            at = ActionType(action_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action_type: {action_type}",
            )

        meta = ACTION_REGISTRY.get(at)
        if meta is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No registry entry for action_type: {action_type}",
            )

        biz_moment = await self._require_moment(moment_id)
        moment_type_code = biz_moment.moment_type or moment_type_for_action(at)

        member = await can_create_activity(
            self.session, moment_id, user_id, capability=meta.get("permission")
        )

        if client_request_id:
            existing = await find_by_client_request_id(self.session, moment_id, client_request_id)
            if existing is not None:
                from app.domains.business.activity.projection_hint import wrap_mutation_response

                return wrap_mutation_response(
                    _to_dto(existing, viewer_id=user_id, member=member, replay=True),
                    op="create",
                )

        from app.domains.business.activity.catalog_validation import (
            validate_payload_against_catalog,
        )

        validate_payload_against_catalog(
            moment_type=moment_type_code,
            action_type=at.value,
            payload=payload,
        )

        event_id = uuid4()
        event = await insert_event(
            self.session,
            event_id=event_id,
            business_moment_id=moment_id,
            user_id=user_id,
            moment_type_code=moment_type_code,
            action_type=at.value,
            title=title,
            subtitle=subtitle,
            payload=payload,
            client_request_id=client_request_id,
            source=source,
        )

        typed_row_id: UUID | None = None
        handler_path = meta["handler"]
        try:
            module = importlib.import_module(handler_path)
            typed_row_id = await module.handle(self.session, event, payload or {})
        except Exception:
            logger.exception("Handler %s failed for event %s", handler_path, event_id)
            raise

        await insert_audit(
            self.session,
            event_id=event_id,
            action="create",
            actor_id=user_id,
            after_payload={"action_type": at.value, "title": title, "payload": payload or {}},
        )

        # Commit correctness-critical work before notify / projection invalidation.
        await self.session.commit()

        from app.domains.business.activity.projection_hint import wrap_mutation_response
        from app.domains.business.activity.types import (
            BUSINESS_OPERATIONS_ACTIONS,
            BUSINESS_RUNWAY_ACTIONS,
        )
        from app.domains.business.projection_cache import (
            invalidate_business_projections_for_action,
        )

        activity = _to_dto(event, viewer_id=user_id, member=member, typed_row_id=typed_row_id)

        from app.domains.shared.deferred_side_effects import schedule_deferred_side_effect

        async def _post_commit_side_effects() -> None:
            from app.core.database import async_session_factory

            if async_session_factory is None:
                raise RuntimeError("async_session_factory unavailable for deferred notify")
            async with async_session_factory() as bg_session:
                if at in BUSINESS_OPERATIONS_ACTIONS or at in BUSINESS_RUNWAY_ACTIONS:
                    from app.domains.business.activity.business_notify_policy import (
                        apply_business_notify_policy,
                    )

                    await apply_business_notify_policy(
                        bg_session,
                        action_type=at,
                        moment_id=moment_id,
                        actor_user_id=user_id,
                        event_id=event_id,
                        typed_row_id=typed_row_id,
                        title=title,
                        payload=payload,
                    )
                await invalidate_business_projections_for_action(
                    user_id,
                    moment_id,
                    action_type=at.value,
                    moment_type=moment_type_code,
                    reason=f"activity:{at.value}",
                )
                await bg_session.commit()

        schedule_deferred_side_effect(
            "business_activity_notify_invalidate",
            _post_commit_side_effects,
            retries=1,
            context={"event_id": str(event_id), "action": at.value},
        )

        return wrap_mutation_response(
            activity, op="create", notify={"deferred": True}
        )

    async def get(self, user_id: UUID, moment_id: UUID, event_id: UUID) -> dict:
        await self._require_moment(moment_id)
        await require_moment_read_access(self.session, moment_id, user_id)
        member = await get_active_member(self.session, moment_id, user_id)
        event = await get_event(self.session, event_id)
        if event is None or event.business_moment_id != moment_id or event.is_voided:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        return _to_dto(event, viewer_id=user_id, member=member)

    async def list(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        action: str | None = None,
        member_id: UUID | None = None,
        status_filter: str = "active",
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
        sort: str = "newest",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        await self._require_moment(moment_id)
        await require_moment_read_access(self.session, moment_id, user_id)
        member = await get_active_member(self.session, moment_id, user_id)

        resolved_status = status_filter if status_filter in ("all", "active", "voided") else "active"
        resolved_sort = sort if sort in ("newest", "oldest") else "newest"

        events, total = await list_events(
            self.session,
            moment_id,
            action=action,
            member=member_id,
            status=resolved_status,  # type: ignore[arg-type]
            date_from=date_from,
            date_to=date_to,
            search=search,
            sort=resolved_sort,  # type: ignore[arg-type]
            page=page,
            page_size=page_size,
        )
        items = [_to_dto(e, viewer_id=user_id, member=member) for e in events]
        return ActivityListResponse(
            items=items,
            total=total,
            page=max(1, page),
            page_size=max(1, min(page_size, 100)),
        ).model_dump(mode="json")

    async def patch(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: UUID,
        patch_data: dict[str, Any],
        *,
        actor_name: str = "You",
    ) -> dict:
        biz_moment = await self._require_moment(moment_id)
        event = await get_event(self.session, event_id)
        if event is None or event.business_moment_id != moment_id or event.is_voided:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

        try:
            at = ActionType(event.action_type)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown action type on event")

        meta = ACTION_REGISTRY.get(at, {})
        if not meta.get("editable", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This activity type is not editable")

        member = await can_edit_activity(self.session, moment_id, user_id, created_by=event.created_by)

        filtered = filter_patch(at, patch_data)
        if not filtered:
            from app.domains.business.activity.projection_hint import wrap_mutation_response

            return wrap_mutation_response(
                _to_dto(event, viewer_id=user_id, member=member), op="patch"
            )

        event_patch = {}
        if "title" in filtered:
            event_patch["title"] = filtered.pop("title")
        if "subtitle" in filtered:
            event_patch["subtitle"] = filtered.pop("subtitle")
        if filtered:
            merged = {**(event.payload or {}), **filtered}
            event_patch["payload"] = merged

        updated = await patch_event(self.session, event_id, event_patch)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

        await self._sync_specialty_from_payload(at, event_id, updated.payload or {})

        await insert_audit(
            self.session,
            event_id=event_id,
            action="edit",
            actor_id=user_id,
            before_payload=event.payload or {},
            after_payload=updated.payload if updated else patch_data,
        )

        moment_type_code = biz_moment.moment_type or moment_type_for_action(at)
        from app.domains.business.activity.projection_hint import wrap_mutation_response
        from app.domains.business.projection_cache import invalidate_business_projections

        await invalidate_business_projections(
            user_id, moment_id, moment_type=moment_type_code, reason="activity:patch"
        )
        return wrap_mutation_response(
            _to_dto(updated, viewer_id=user_id, member=member), op="patch"
        )

    async def delete_soft(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: UUID,
        *,
        actor_name: str = "You",
    ) -> dict:
        biz_moment = await self._require_moment(moment_id)
        event = await get_event(self.session, event_id)
        if event is None or event.business_moment_id != moment_id or event.is_voided:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

        try:
            at = ActionType(event.action_type)
        except ValueError:
            at = None

        if at:
            meta = ACTION_REGISTRY.get(at, {})
            if not meta.get("deletable", False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This activity type is not deletable")

        await can_delete_activity(self.session, moment_id, user_id, created_by=event.created_by)

        voided = await soft_void_event(self.session, event_id)
        if not voided:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

        await self._void_specialty_rows(event_id)

        await insert_audit(
            self.session,
            event_id=event_id,
            action="delete",
            actor_id=user_id,
            before_payload={"is_voided": False},
            after_payload={"is_voided": True},
        )

        moment_type_code = biz_moment.moment_type or "TEAM_OPERATIONS"
        from app.domains.business.activity.projection_hint import wrap_mutation_response
        from app.domains.business.projection_cache import invalidate_business_projections

        await invalidate_business_projections(
            user_id, moment_id, moment_type=moment_type_code, reason="activity:delete"
        )
        member = await get_active_member(self.session, moment_id, user_id)
        voided_event = await get_event(self.session, event_id)
        if voided_event is None:
            return wrap_mutation_response(
                {
                    "event_id": str(event_id),
                    "business_moment_id": str(moment_id),
                    "action_type": event.action_type,
                    "title": event.title,
                    "is_voided": True,
                    "occurred_at": event.occurred_at.isoformat()
                    if getattr(event, "occurred_at", None)
                    else None,
                },
                op="delete",
            )
        return wrap_mutation_response(
            _to_dto(voided_event, viewer_id=user_id, member=member), op="delete"
        )

    async def _sync_specialty_from_payload(
        self, action_type: ActionType, event_id: UUID, payload: dict[str, Any]
    ) -> None:
        """Keep typed child rows aligned when patchable fields change projection inputs."""
        from decimal import Decimal

        from sqlalchemy import select

        from app.domains.business.activity.handlers._helpers import minor_to_decimal
        from app.domains.business.models import (
            OperationsImprovements,
            OperationsIssues,
            OperationsSpendEntries,
            OperationsVendorUpdates,
        )

        if action_type == ActionType.SPEND_ENTRY:
            row = (
                await self.session.execute(
                    select(OperationsSpendEntries).where(OperationsSpendEntries.event_id == event_id)
                )
            ).scalar_one_or_none()
            if row is None:
                return
            currency = str(payload.get("currency_code") or payload.get("currency") or row.currency or "INR")
            if payload.get("amount_minor") is not None:
                amount_minor = int(payload["amount_minor"])
                amount = minor_to_decimal(amount_minor, currency=currency)
                row.amount_minor = amount_minor
                row.amount = amount
                row.amount_in_operating_currency = amount * Decimal(
                    str(row.exchange_rate_to_operating_currency or 1)
                )
            elif payload.get("amount") is not None:
                amount = Decimal(str(payload["amount"]))
                row.amount = amount
                row.amount_in_operating_currency = amount * Decimal(
                    str(row.exchange_rate_to_operating_currency or 1)
                )
            if payload.get("spend_category"):
                row.spend_category = str(payload["spend_category"])
            if payload.get("description") is not None:
                row.description = payload.get("description")
            if payload.get("currency") or payload.get("currency_code"):
                row.currency = currency
            if payload.get("vendor_name") is not None:
                row.vendor_name = (str(payload.get("vendor_name") or "").strip() or None)
            if payload.get("payment_method") or payload.get("payment_status") is not None:
                from app.domains.business.activity.handlers.business_operations.spend_entry import (
                    _normalize_payment,
                )

                method, status, paid_minor, due_minor = _normalize_payment(
                    amount_minor=int(row.amount_minor or 0),
                    payment_method=payload.get("payment_method") or row.payment_method,
                    payment_status=payload.get("payment_status") or row.payment_status,
                    amount_paid_raw=payload.get("amount_paid_minor", row.amount_paid_minor),
                )
                row.payment_method = method
                row.payment_status = status
                row.amount_paid_minor = paid_minor
                payload["payment_method"] = method
                payload["payment_status"] = status
                payload["amount_paid_minor"] = paid_minor
                payload["amount_due_minor"] = due_minor
            await self.session.flush()
            return

        if action_type == ActionType.ISSUE_RISK:
            row = (
                await self.session.execute(
                    select(OperationsIssues).where(OperationsIssues.event_id == event_id)
                )
            ).scalar_one_or_none()
            if row is None:
                return
            if payload.get("severity"):
                sev = str(payload["severity"]).lower()
                if sev in {"low", "medium", "high", "critical"}:
                    row.severity = sev
            status_val = payload.get("issue_status") or payload.get("status")
            if status_val:
                st = str(status_val).lower()
                if st in {"open", "investigating", "resolved", "archived"}:
                    row.issue_status = st
            if payload.get("description") is not None:
                row.description = payload.get("description")
            if payload.get("impact_area"):
                row.impact_area = str(payload["impact_area"])
            if payload.get("title"):
                row.issue_title = str(payload["title"])
            await self.session.flush()
            return

        if action_type == ActionType.VENDOR_UPDATE:
            row = (
                await self.session.execute(
                    select(OperationsVendorUpdates).where(OperationsVendorUpdates.event_id == event_id)
                )
            ).scalar_one_or_none()
            if row is None:
                return
            if payload.get("vendor_status"):
                row.vendor_status = str(payload["vendor_status"])
            if payload.get("impact_level"):
                row.impact_level = str(payload["impact_level"])
            if payload.get("description") is not None:
                row.description = payload.get("description")
            await self.session.flush()
            return

        if action_type == ActionType.OPERATIONAL_IMPROVEMENT:
            row = (
                await self.session.execute(
                    select(OperationsImprovements).where(OperationsImprovements.event_id == event_id)
                )
            ).scalar_one_or_none()
            if row is None:
                return
            if payload.get("improvement_status"):
                row.improvement_status = str(payload["improvement_status"])
            if payload.get("description") is not None:
                row.description = payload.get("description")
            await self.session.flush()

    async def _void_specialty_rows(self, event_id: UUID) -> None:
        """Keep pulse specialty counts honest when activity is soft-deleted."""
        from sqlalchemy import update

        from app.domains.business.models import (
            OperationsApprovalRequests,
            OperationsImprovements,
            OperationsIssues,
            OperationsSpendEntries,
            OperationsVendorUpdates,
            RunwayCashInflows,
            RunwayExpenseBurns,
            RunwayFinancialUpdates,
            RunwayRisks,
            RunwayStrategicDecisions,
            TeamActivities,
            TeamApprovalRequests,
            TeamEscalations,
            TeamIssueRisks,
            TeamMeetings,
            TeamMemberUpdates,
            TeamParticipation,
            TeamRecognitions,
            TeamUpdates,
        )

        for model in (
            TeamIssueRisks,
            TeamApprovalRequests,
            TeamEscalations,
            TeamRecognitions,
            TeamMeetings,
            TeamParticipation,
            TeamActivities,
            TeamMemberUpdates,
            TeamUpdates,
            OperationsSpendEntries,
            OperationsVendorUpdates,
            OperationsApprovalRequests,
            OperationsIssues,
            OperationsImprovements,
            RunwayCashInflows,
            RunwayExpenseBurns,
            RunwayRisks,
            RunwayStrategicDecisions,
            RunwayFinancialUpdates,
        ):
            if not hasattr(model, "is_voided") or not hasattr(model, "event_id"):
                continue
            await self.session.execute(
                update(model)
                .where(model.event_id == event_id, model.is_voided.is_(False))
                .values(is_voided=True)
            )
