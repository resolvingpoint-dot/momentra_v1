"""Post-create notification policy for all Business Quick Add actions.

Writes ``business_notifications`` rows (in_app + optional push) and enqueues
push delivery. Critical runway risks also set ``action_center`` metadata for clients.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.types import (
    BUSINESS_OPERATIONS_ACTIONS,
    BUSINESS_RUNWAY_ACTIONS,
    ActionType,
)
from app.domains.business.models import BusinessMomentMembers, BusinessNotifications

logger = logging.getLogger(__name__)

_MANAGER_ROLES = {
    "operations owner",
    "operations lead",
    "budget owner",
    "budget controller",
    "approver",
    "team lead",
}

_FINANCE_ROLES = {
    "finance lead",
    "runway owner",
    "budget owner",
    "budget controller",
    "financial contributor",
}

_LEADERSHIP_ROLES = {
    "runway owner",
    "operations owner",
    "operations lead",
    "team lead",
    "finance lead",
    "approver",
}

# Default burn threshold in minor units (₹50,000) when moment has no config.
_DEFAULT_BURN_NOTIFY_THRESHOLD_MINOR = 5_000_000


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "on"}:
        return True
    if s in {"0", "false", "no", "off"}:
        return False
    return default


def _uuid_list(raw: Any) -> list[UUID]:
    if raw is None:
        return []
    items = raw if isinstance(raw, list) else [raw]
    out: list[UUID] = []
    for item in items:
        if item is None or item == "":
            continue
        try:
            out.append(UUID(str(item)))
        except (TypeError, ValueError):
            continue
    return out


async def _member_user_map(
    session: AsyncSession, moment_id: UUID
) -> dict[UUID, UUID]:
    result = await session.execute(
        select(BusinessMomentMembers.member_id, BusinessMomentMembers.user_id).where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.member_status.in_(("active", "configured")),
            BusinessMomentMembers.user_id.is_not(None),
        )
    )
    return {row.member_id: row.user_id for row in result.all() if row.user_id}


async def _users_by_roles(
    session: AsyncSession, moment_id: UUID, roles: set[str]
) -> set[UUID]:
    result = await session.execute(
        select(BusinessMomentMembers.user_id, BusinessMomentMembers.role).where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.member_status.in_(("active", "configured")),
            BusinessMomentMembers.user_id.is_not(None),
        )
    )
    out: set[UUID] = set()
    for row in result.all():
        role = (row.role or "").strip().lower()
        if role in roles or any(r in role for r in ("owner", "lead", "admin")):
            if row.user_id:
                out.add(row.user_id)
    return out


async def _manager_user_ids(session: AsyncSession, moment_id: UUID) -> set[UUID]:
    return await _users_by_roles(session, moment_id, _MANAGER_ROLES)


async def _finance_user_ids(session: AsyncSession, moment_id: UUID) -> set[UUID]:
    return await _users_by_roles(session, moment_id, _FINANCE_ROLES)


async def _leadership_user_ids(session: AsyncSession, moment_id: UUID) -> set[UUID]:
    return await _users_by_roles(session, moment_id, _LEADERSHIP_ROLES)


async def _admin_user_ids(session: AsyncSession, moment_id: UUID) -> set[UUID]:
    """Workspace admins: owners + leads."""
    return await _users_by_roles(
        session,
        moment_id,
        {"runway owner", "operations owner", "team lead", "finance lead"},
    )


async def _resolve_user_ids(
    session: AsyncSession,
    moment_id: UUID,
    *,
    member_ids: list[UUID] | None = None,
    user_ids: list[UUID] | None = None,
) -> set[UUID]:
    member_map = await _member_user_map(session, moment_id)
    recipients: set[UUID] = set(user_ids or [])
    for mid in member_ids or []:
        uid = member_map.get(mid)
        if uid:
            recipients.add(uid)
    known_users = set(member_map.values())
    for uid in user_ids or []:
        if uid in known_users:
            recipients.add(uid)
        elif uid in member_map:
            mapped = member_map.get(uid)
            if mapped:
                recipients.add(mapped)
    return {u for u in recipients if u}


def _insert_note(
    session: AsyncSession,
    *,
    moment_id: UUID,
    recipient_user_id: UUID,
    notification_type: str,
    source_table: str,
    source_record_id: UUID,
    title: str,
    message: str,
    priority: str = "medium",
    delivery_channel: str = "in_app",
    notification_status: str = "sent",
    deep_link: str | None = None,
) -> BusinessNotifications:
    meta = {}
    if deep_link:
        meta["deep_link"] = deep_link
    note = BusinessNotifications(
        moment_id=moment_id,
        recipient_user_id=recipient_user_id,
        notification_type=notification_type,
        source_table=source_table,
        source_record_id=source_record_id,
        title=title[:500],
        message=message,
        priority=priority if priority in {"low", "medium", "high", "critical"} else "medium",
        delivery_channel=delivery_channel,
        notification_status=notification_status,
    )
    # Store deep_link in message suffix for clients that don't read extra columns
    if deep_link and deep_link not in (message or ""):
        note.message = f"{message}\n[deeplink:{deep_link}]"
    session.add(note)
    return note


def _enqueue_push(notification_id: UUID) -> None:
    try:
        from app.workers.tasks.notifications import deliver_notification

        deliver_notification.delay(str(notification_id))
    except Exception:
        logger.exception("Failed to enqueue push for %s", notification_id)


async def apply_business_notify_policy(
    session: AsyncSession,
    *,
    action_type: ActionType,
    moment_id: UUID,
    actor_user_id: UUID,
    event_id: UUID,
    typed_row_id: UUID | None,
    title: str,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Create inbox (+ optional push) rows. Returns notify summary for clients."""
    payload = payload or {}
    source_id = typed_row_id or event_id
    deep_link = f"momentra://business/{moment_id}/activity/{event_id}"

    try:
        if action_type in BUSINESS_OPERATIONS_ACTIONS:
            return await _apply_ops(
                session,
                action_type=action_type,
                moment_id=moment_id,
                actor_user_id=actor_user_id,
                event_id=event_id,
                source_id=source_id,
                title=title,
                payload=payload,
                deep_link=deep_link,
            )
        if action_type in BUSINESS_RUNWAY_ACTIONS:
            return await _apply_runway(
                session,
                action_type=action_type,
                moment_id=moment_id,
                actor_user_id=actor_user_id,
                event_id=event_id,
                source_id=source_id,
                title=title,
                payload=payload,
                deep_link=deep_link,
            )
        return {"notifications_created": 0, "recipient_user_ids": []}
    except Exception:
        logger.exception("Business notify policy failed for event %s", event_id)
        return {"notifications_created": 0, "recipient_user_ids": [], "error": True}


async def _finalize(
    session: AsyncSession,
    *,
    moment_id: UUID,
    recipients: set[UUID],
    actor_user_id: UUID,
    notification_type: str,
    source_id: UUID,
    title: str,
    message: str,
    priority: str,
    push: bool = False,
    action_center: bool = False,
    deep_link: str | None = None,
) -> dict[str, Any]:
    recipients.discard(actor_user_id)
    created = 0
    push_ids: list[str] = []
    for uid in recipients:
        note = _insert_note(
            session,
            moment_id=moment_id,
            recipient_user_id=uid,
            notification_type=notification_type,
            source_table="business_activity_events",
            source_record_id=source_id,
            title=title,
            message=message,
            priority=priority,
            delivery_channel="in_app",
            notification_status="sent",
            deep_link=deep_link if action_center else None,
        )
        created += 1
        if push:
            push_note = _insert_note(
                session,
                moment_id=moment_id,
                recipient_user_id=uid,
                notification_type=notification_type,
                source_table="business_activity_events",
                source_record_id=source_id,
                title=title,
                message=message,
                priority=priority,
                delivery_channel="push",
                notification_status="queued",
                deep_link=deep_link,
            )
            await session.flush()
            nid = getattr(push_note, "notification_id", None)
            if nid:
                _enqueue_push(nid)
                push_ids.append(str(nid))
            created += 1
    if created:
        await session.flush()
    return {
        "notifications_created": created,
        "recipient_user_ids": [str(u) for u in recipients],
        "notification_type": notification_type,
        "push_queued": push_ids,
        "action_center": action_center,
        "deep_link": deep_link if action_center else None,
        "priority": priority,
    }


async def _apply_ops(
    session: AsyncSession,
    *,
    action_type: ActionType,
    moment_id: UUID,
    actor_user_id: UUID,
    event_id: UUID,
    source_id: UUID,
    title: str,
    payload: dict[str, Any],
    deep_link: str,
) -> dict[str, Any]:
    recipients: set[UUID] = set()
    notification_type = f"ops.{action_type.value.lower()}"
    message = title
    priority = str(payload.get("priority") or "medium").lower()
    if priority == "urgent":
        priority = "high"
    push = False
    action_center = False

    if action_type == ActionType.OPS_APPROVAL_REQUEST:
        approver_member_ids = _uuid_list(payload.get("approver_ids"))
        if payload.get("approver_id"):
            approver_member_ids = _uuid_list([payload.get("approver_id")]) + approver_member_ids
        recipients |= await _resolve_user_ids(session, moment_id, member_ids=approver_member_ids)
        notification_type = "ops.approval_request"
        message = f"Approval requested: {title}"
        priority = "high" if priority not in {"high", "critical"} else priority
        push = True
        action_center = True
    elif action_type == ActionType.OPERATIONAL_IMPROVEMENT:
        owner_ids = _uuid_list(payload.get("owner_id"))
        recipients |= await _resolve_user_ids(session, moment_id, member_ids=owner_ids)
        if _as_bool(payload.get("notify_managers")):
            recipients |= await _manager_user_ids(session, moment_id)
        notify_extra = _uuid_list(payload.get("notify_user_ids")) + _uuid_list(
            payload.get("notify_member_ids")
        )
        recipients |= await _resolve_user_ids(
            session, moment_id, member_ids=notify_extra, user_ids=notify_extra
        )
        notification_type = "ops.improvement_assigned"
        message = f"Improvement assigned: {title}"
    elif action_type == ActionType.ISSUE_RISK:
        owner_ids = _uuid_list(payload.get("owner_id"))
        recipients |= await _resolve_user_ids(session, moment_id, member_ids=owner_ids)
        if _as_bool(payload.get("notify_managers")):
            recipients |= await _manager_user_ids(session, moment_id)
        severity = str(payload.get("severity") or "").lower()
        if severity == "critical":
            recipients |= await _admin_user_ids(session, moment_id)
            push = True
            action_center = True
            priority = "critical"
        notification_type = "ops.issue_assigned"
        message = f"Issue assigned: {title}"
    elif action_type == ActionType.SPEND_ENTRY:
        if _as_bool(payload.get("notify_managers")):
            recipients |= await _manager_user_ids(session, moment_id)
        notification_type = "ops.spend_entry"
        message = f"Spend recorded: {title}"
    elif action_type == ActionType.VENDOR_UPDATE:
        event_kind = str(payload.get("vendor_event_type") or "").lower()
        default_managers = event_kind in {"vendor_issue", "contract_renewal"}
        if _as_bool(payload.get("notify_managers"), default=default_managers):
            recipients |= await _manager_user_ids(session, moment_id)
        notify_extra = _uuid_list(payload.get("notify_user_ids")) + _uuid_list(
            payload.get("notify_member_ids")
        )
        recipients |= await _resolve_user_ids(
            session, moment_id, member_ids=notify_extra, user_ids=notify_extra
        )
        notification_type = "ops.vendor_update"
        message = f"Vendor update: {title}"
    elif action_type == ActionType.OPS_GENERAL_UPDATE:
        if _as_bool(payload.get("notify_managers")):
            recipients |= await _manager_user_ids(session, moment_id)
        notify_extra = _uuid_list(payload.get("notify_user_ids")) + _uuid_list(
            payload.get("notify_member_ids")
        )
        recipients |= await _resolve_user_ids(
            session, moment_id, member_ids=notify_extra, user_ids=notify_extra
        )
        notification_type = "ops.general_update"
        message = f"Update: {title}"
    else:
        return {"notifications_created": 0, "recipient_user_ids": []}

    return await _finalize(
        session,
        moment_id=moment_id,
        recipients=recipients,
        actor_user_id=actor_user_id,
        notification_type=notification_type,
        source_id=source_id,
        title=title,
        message=message,
        priority=priority,
        push=push,
        action_center=action_center,
        deep_link=deep_link,
    )


async def _apply_runway(
    session: AsyncSession,
    *,
    action_type: ActionType,
    moment_id: UUID,
    actor_user_id: UUID,
    event_id: UUID,
    source_id: UUID,
    title: str,
    payload: dict[str, Any],
    deep_link: str,
) -> dict[str, Any]:
    recipients: set[UUID] = set()
    notification_type = f"runway.{action_type.value.lower()}"
    message = title
    priority = "medium"
    push = False
    action_center = False

    if action_type == ActionType.CASH_INFLOW:
        # Activity feed always; optional finance admins via toggle
        if _as_bool(payload.get("notify_finance_admins")):
            recipients |= await _finance_user_ids(session, moment_id)
        notification_type = "runway.cash_inflow"
        message = f"Cash inflow: {title}"

    elif action_type == ActionType.EXPENSE_BURN:
        amount_minor = 0
        try:
            amount_minor = int(payload.get("amount_minor") or 0)
        except (TypeError, ValueError):
            amount_minor = 0
        threshold = _DEFAULT_BURN_NOTIFY_THRESHOLD_MINOR
        over = amount_minor >= threshold
        if over and _as_bool(payload.get("notify_finance_owner"), default=True):
            recipients |= await _finance_user_ids(session, moment_id)
            push = True
            priority = "high"
        notification_type = "runway.expense_burn"
        message = f"Burn expense recorded: {title or 'Expense'}"

    elif action_type == ActionType.RUNWAY_RISK:
        if _as_bool(payload.get("notify_owner"), default=True):
            owner_ids = _uuid_list(payload.get("owner_id"))
            recipients |= await _resolve_user_ids(session, moment_id, member_ids=owner_ids)
        severity = str(payload.get("severity") or "").lower()
        if severity == "critical":
            recipients |= await _admin_user_ids(session, moment_id)
            push = True
            action_center = True
            priority = "critical"
            notification_type = "runway.risk_critical"
            message = f"Critical runway risk: {title}"
        else:
            notification_type = "runway.risk"
            message = f"Runway risk: {title}"
            priority = severity if severity in {"low", "medium", "high", "critical"} else "medium"

    elif action_type == ActionType.FINANCIAL_UPDATE:
        update_type = str(payload.get("update_type") or "").lower()
        # Notify on significant changes: cash, threshold, or burn
        significant = update_type in {
            "cash_available",
            "runway_threshold",
            "monthly_burn",
        }
        if significant and _as_bool(payload.get("share_update"), default=True):
            recipients |= await _finance_user_ids(session, moment_id)
            if update_type in {"runway_threshold", "monthly_burn"}:
                push = True
                priority = "high"
        notification_type = "runway.financial_update"
        message = f"Financial update ({update_type}): {title or 'Update'}"

    elif action_type == ActionType.STRATEGIC_DECISION:
        owner_ids = _uuid_list(payload.get("decision_owner_id")) + _uuid_list(
            payload.get("owner_id")
        )
        recipients |= await _resolve_user_ids(session, moment_id, member_ids=owner_ids)
        if _as_bool(payload.get("notify_leadership"), default=True):
            recipients |= await _leadership_user_ids(session, moment_id)
        approvers = _uuid_list(payload.get("notify_approver_ids"))
        recipients |= await _resolve_user_ids(session, moment_id, member_ids=approvers)
        notification_type = "runway.strategic_decision"
        message = f"Strategic decision: {title}"
        push = bool(approvers)
    else:
        return {"notifications_created": 0, "recipient_user_ids": []}

    return await _finalize(
        session,
        moment_id=moment_id,
        recipients=recipients,
        actor_user_id=actor_user_id,
        notification_type=notification_type,
        source_id=source_id,
        title=title,
        message=message,
        priority=priority,
        push=push,
        action_center=action_center,
        deep_link=deep_link,
    )


# Back-compat alias
async def apply_ops_notify_policy(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await apply_business_notify_policy(*args, **kwargs)
