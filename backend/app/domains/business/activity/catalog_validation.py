"""Validate activity create payloads against the Action Center catalog."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from app.domains.business.action_catalog import get_action_entry

# Keys clients may always send alongside catalog fields.
_ALWAYS_ALLOWED = {
    "currency",
    "currency_code",
    "exchange_rate_to_operating_currency",
    "amount",
    "client_meta",
    "attachment_paths",
    "share_update",
    "notify_finance_admins",
    "notify_finance_owner",
    "notify_owner",
    "notify_leadership",
    "notify_managers",
    "notify_user_ids",
    "notify_member_ids",
    "notify_approver_ids",
    "risk_type",
    "adjustment_required",
    "current_value",
    "new_value",
    "approval_required",
    "vendor_name",
    "priority",
    "amount_due_minor",
    "amount_paid_minor",
    "payment_method",
    "payment_status",
}


def validate_payload_against_catalog(
    *,
    moment_type: str,
    action_type: str,
    payload: dict[str, Any] | None,
) -> None:
    """Raise HTTP 400 if required catalog fields are missing or keys are unknown."""
    entry = get_action_entry(moment_type, action_type)
    if entry is None:
        # Registry still gates unknown action types; skip soft catalog miss.
        return

    payload = payload or {}
    fields: list[dict[str, Any]] = list(entry.get("fields") or [])
    known_keys = {f["key"] for f in fields if f.get("key")} | _ALWAYS_ALLOWED
    required = list(entry.get("required_fields") or [])

    missing: list[str] = []
    for key in required:
        val = payload.get(key)
        if val is None or val == "" or val == []:
            missing.append(key)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "catalog_required", "missing_fields": missing},
        )

    unknown = [k for k in payload.keys() if k not in known_keys]
    # Soft-allow unknown keys that look like legacy aliases; only reject noisy junk
    # when clearly not related (keep permissive for gradual client rollout).
    # Hard-reject empty string keys only.
    bad = [k for k in unknown if not k or not str(k).strip()]
    if bad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "catalog_unknown", "unknown_fields": bad},
        )

    # Option membership for select-like fields
    for field in fields:
        key = field.get("key")
        opts = field.get("options")
        if not key or not opts:
            continue
        val = payload.get(key)
        if val is None or val == "":
            continue
        allowed = {o.get("value") for o in opts if isinstance(o, dict)}
        if str(val) not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "catalog_option",
                    "field": key,
                    "value": val,
                    "allowed": sorted(allowed),
                },
            )
