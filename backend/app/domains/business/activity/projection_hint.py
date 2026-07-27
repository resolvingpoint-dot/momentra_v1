"""Build cheap projection_hint for Business activity mutations (no SQL rebuild)."""
from __future__ import annotations

from typing import Any, Literal


def build_projection_hint(
    activity: dict[str, Any],
    *,
    op: Literal["create", "patch", "delete"] = "create",
) -> dict[str, Any]:
    """Hint for clients to patch Pulse / Moments / Activity without waiting for Celery.

    Celery + Redis stale-mark remain the source of truth for reconcile.
    """
    delta = -1 if op == "delete" else (0 if op == "patch" else 1)
    action = str(activity.get("action_type") or "").upper()
    counters: dict[str, int] = {"activity_delta": delta}
    # Lightweight family bumps — clients apply if the KPI exists.
    if "ISSUE" in action or action.endswith("_ISSUE"):
        counters["open_issues_delta"] = delta
    if "APPROVAL" in action:
        counters["pending_approvals_delta"] = delta
    if "ESCALAT" in action:
        counters["escalation_delta"] = delta
    if "RECOGN" in action:
        counters["recognition_delta"] = delta

    event = {
        "event_id": activity.get("event_id"),
        "action_type": activity.get("action_type"),
        "title": activity.get("title"),
        "subtitle": activity.get("subtitle"),
        "occurred_at": activity.get("occurred_at"),
        "client_request_id": activity.get("client_request_id"),
        "source": activity.get("source"),
        "is_voided": bool(activity.get("is_voided")),
        "business_moment_id": activity.get("business_moment_id"),
        "moment_type_code": activity.get("moment_type_code"),
    }
    return {
        "op": op,
        "activity_event": event,
        "counters": counters,
        # Placeholders for future richer hints; clients ignore unknown keys.
        "pulse": {"recent_activity_prepend": event if op != "delete" else None},
        "moments": {"timeline_prepend": event if op != "delete" else None},
    }


def wrap_mutation_response(
    activity: dict[str, Any],
    *,
    op: Literal["create", "patch", "delete"] = "create",
) -> dict[str, Any]:
    return {
        "activity": activity,
        "projection_hint": build_projection_hint(activity, op=op),
    }
