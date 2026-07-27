"""Business Operations answer/member/allocation normalizers."""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.domains.business.setup.business_operations_permissions import (
    PERMISSION_VERSION_V1,
    SUPPORTED_ROLES_V1,
    default_profile_for_role,
)
from app.domains.business.setup.normalizers import normalize_answers as shared_field_aliases

OPERATIONS_SCOPE_CANONICAL = {
    "GENERAL_OPERATIONS",
    "DEPARTMENT",
    "PROJECT_PORTFOLIO",
    "VENDOR_OPERATIONS",
    "RETAIL_OPERATIONS",
    "SERVICE_OPERATIONS",
    "MANUFACTURING_OPERATIONS",
    "CUSTOM",
}

OPERATING_MODEL_CANONICAL = {
    "CENTRALIZED",
    "DECENTRALIZED",
    "HYBRID",
    "PROJECT_BASED",
    "FUNCTIONAL",
    "CUSTOM",
}

REVIEW_CYCLE_CANONICAL = {"WEEKLY", "BIWEEKLY", "MONTHLY", "QUARTERLY", "CUSTOM"}
VENDOR_DEPENDENCY_CANONICAL = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
APPROVAL_MODEL_CANONICAL = {
    "NONE",
    "OWNER_ONLY",
    "SINGLE_APPROVER",
    "MULTI_APPROVER",
    "THRESHOLD_BASED",
    "ROLE_BASED",
}
ISSUE_SENSITIVITY_CANONICAL = {"LOW", "NORMAL", "HIGH", "CRITICAL"}
MONITORING_CANONICAL = {"LIGHT", "STANDARD", "DETAILED", "REAL_TIME"}
VISIBILITY_CANONICAL = {"PRIVATE", "TEAM", "LEADERSHIP", "ORGANIZATION"}
ALLOCATION_MODES = {"FIXED_AMOUNT", "PERCENTAGE"}

INVITE_METHODS = {"EMAIL", "SMS", "WHATSAPP", "QR", "SHARE", "COPY_LINK", "NATIVE_SHARE"}

# Compatibility mirrors for NOT NULL legacy SQL columns (not semantic false aliases for draft).
_SCOPE_TO_SQL = {
    "GENERAL_OPERATIONS": "department",
    "DEPARTMENT": "department",
    "PROJECT_PORTFOLIO": "department",
    "VENDOR_OPERATIONS": "warehouse",
    "RETAIL_OPERATIONS": "store",
    "SERVICE_OPERATIONS": "clinic",
    "MANUFACTURING_OPERATIONS": "factory",
    "CUSTOM": "custom",
}
_MODEL_TO_SQL = {
    "CENTRALIZED": "budget_driven",
    "DECENTRALIZED": "vendor_driven",
    "HYBRID": "balanced_operations",
    "PROJECT_BASED": "performance_driven",
    "FUNCTIONAL": "compliance_driven",
    "CUSTOM": "balanced_operations",
}


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off", ""}:
        return False
    return default


def _as_minor(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _upper_enum(value: Any, allowed: set[str]) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    return key if key in allowed else None


def scope_to_sql(canonical: str | None) -> str:
    return _SCOPE_TO_SQL.get((canonical or "CUSTOM").upper(), "custom")


def model_to_sql(canonical: str | None) -> str:
    return _MODEL_TO_SQL.get((canonical or "CUSTOM").upper(), "balanced_operations")


def normalize_member(raw: dict[str, Any], *, owner_user_id: str | None = None) -> dict[str, Any]:
    role = str(raw.get("role") or "MEMBER").upper()
    if role not in SUPPORTED_ROLES_V1:
        role = "MEMBER"
    is_owner = role == "OWNER" and owner_user_id and str(raw.get("user_id") or "") == str(owner_user_id)
    invite_method = str(raw.get("invite_method") or "EMAIL").upper()
    if invite_method not in INVITE_METHODS:
        invite_method = "EMAIL"
    return {
        "local_id": str(raw.get("local_id") or uuid4()),
        "user_id": str(raw["user_id"]) if raw.get("user_id") else None,
        "name": str(raw.get("name") or role),
        "email": (str(raw["email"]).strip() if raw.get("email") else None),
        "phone": (str(raw["phone"]).strip() if raw.get("phone") else None),
        "role": role,
        "permission_profile": raw.get("permission_profile") or default_profile_for_role(role),
        "permission_version": int(raw.get("permission_version") or PERMISSION_VERSION_V1),
        "invite_method": invite_method,
        "invite_status": (
            "ACCEPTED"
            if is_owner
            else str(raw.get("invite_status") or "DRAFT").upper()
        ),
        "is_approver": _as_bool(raw.get("is_approver")) or role == "APPROVER",
        "is_budget_controller": _as_bool(raw.get("is_budget_controller"))
        or role == "BUDGET_CONTROLLER",
        "is_operations_lead": _as_bool(raw.get("is_operations_lead")) or role == "OPERATIONS_LEAD",
        "is_vendor_manager": _as_bool(raw.get("is_vendor_manager")) or role == "VENDOR_MANAGER",
        "is_observer": _as_bool(raw.get("is_observer")) or role == "OBSERVER",
    }


def inject_owner_member(
    members: list[dict[str, Any]],
    owner_user_id: str,
    *,
    owner_display_name: str | None = None,
) -> list[dict[str, Any]]:
    cleaned = [
        m
        for m in members
        if not (
            str(m.get("user_id") or "") == str(owner_user_id) or m.get("role") == "OWNER"
        )
    ]
    display = (owner_display_name or "").strip() or "You"
    owner = {
        "local_id": "owner",
        "user_id": str(owner_user_id),
        "name": display,
        "email": None,
        "phone": None,
        "role": "OWNER",
        "permission_profile": "OWNER_V1",
        "permission_version": PERMISSION_VERSION_V1,
        "invite_method": "EMAIL",
        "invite_status": "ACCEPTED",
        "is_approver": False,
        "is_budget_controller": False,
        "is_operations_lead": False,
        "is_vendor_manager": False,
        "is_observer": False,
    }
    return [owner, *cleaned]


def dedupe_members(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_email: set[str] = set()
    seen_phone: set[str] = set()
    seen_local: set[str] = set()
    out: list[dict[str, Any]] = []
    for m in members:
        local = str(m.get("local_id") or "")
        email = (m.get("email") or "").strip().lower()
        phone = (m.get("phone") or "").strip()
        if local and local in seen_local:
            continue
        if email and email in seen_email:
            continue
        if phone and phone in seen_phone:
            continue
        if local:
            seen_local.add(local)
        if email:
            seen_email.add(email)
        if phone:
            seen_phone.add(phone)
        out.append(m)
    return out


def resolve_allocations(
    *,
    monthly_budget_minor: int | None,
    allocations: list[dict[str, Any]],
    allocation_mode: str,
) -> list[dict[str, Any]]:
    """Resolve amount_minor for every allocation; deterministic remainder to first id."""
    mode = (allocation_mode or "FIXED_AMOUNT").upper()
    budget = int(monthly_budget_minor or 0)
    normalized: list[dict[str, Any]] = []
    for raw in allocations:
        if not isinstance(raw, dict):
            continue
        aid = str(raw.get("allocation_id") or uuid4())
        pct = _as_minor(raw.get("percentage"))
        amount = _as_minor(raw.get("amount_minor"))
        item = {
            "allocation_id": aid,
            "category_code": str(raw.get("category_code") or "custom"),
            "label": str(raw.get("label") or raw.get("category_code") or "Allocation"),
            "amount_minor": amount if amount is not None else 0,
            "percentage": pct,
            "owner_id": raw.get("owner_id"),
            "notes": raw.get("notes"),
        }
        normalized.append(item)

    normalized.sort(key=lambda x: x["allocation_id"])

    if mode == "PERCENTAGE" and budget >= 0 and normalized:
        assigned = 0
        for i, item in enumerate(normalized):
            pct = int(item.get("percentage") or 0)
            if i < len(normalized) - 1:
                amt = (budget * pct) // 100
                item["amount_minor"] = amt
                assigned += amt
            else:
                item["amount_minor"] = max(0, budget - assigned)
    return normalized


def compute_derived_preview(answers: dict[str, Any]) -> dict[str, Any]:
    budget = int(answers.get("monthly_budget_minor") or 0)
    allocations = answers.get("budget_allocations") or []
    allocated = 0
    if isinstance(allocations, list):
        for a in allocations:
            if isinstance(a, dict):
                allocated += int(a.get("amount_minor") or 0)
    members = answers.get("members") or []
    member_count = len(members) if isinstance(members, list) else 0
    approver_count = 0
    if isinstance(members, list):
        approver_count = sum(
            1
            for m in members
            if isinstance(m, dict)
            and (m.get("is_approver") or str(m.get("role") or "").upper() == "APPROVER")
        )
    percent = int((allocated * 100) // budget) if budget > 0 else 0
    return {
        "allocated_budget_minor": allocated,
        "unallocated_budget_minor": max(0, budget - allocated),
        "allocation_percent": percent,
        "approver_count": approver_count,
        "member_count": member_count,
    }


def normalize_operations_answers(
    answers: dict[str, Any] | None,
    *,
    owner_user_id: str | None = None,
    owner_display_name: str | None = None,
) -> dict[str, Any]:
    raw = shared_field_aliases(answers)
    out = dict(raw)

    currency = (
        out.get("operating_currency_code")
        or out.get("default_currency_code")
        or out.get("currency")
    )
    if currency:
        out["operating_currency_code"] = str(currency).upper()

    out["operations_scope"] = _upper_enum(out.get("operations_scope"), OPERATIONS_SCOPE_CANONICAL)
    out["operating_model"] = _upper_enum(out.get("operating_model"), OPERATING_MODEL_CANONICAL)
    out["review_cycle"] = _upper_enum(out.get("review_cycle"), REVIEW_CYCLE_CANONICAL)
    out["vendor_dependency_level"] = _upper_enum(
        out.get("vendor_dependency_level"), VENDOR_DEPENDENCY_CANONICAL
    )
    out["approval_model"] = _upper_enum(out.get("approval_model"), APPROVAL_MODEL_CANONICAL)
    out["issue_sensitivity"] = _upper_enum(out.get("issue_sensitivity"), ISSUE_SENSITIVITY_CANONICAL)
    out["monitoring_level"] = _upper_enum(out.get("monitoring_level"), MONITORING_CANONICAL)
    out["operational_visibility"] = _upper_enum(
        out.get("operational_visibility") or out.get("visibility"), VISIBILITY_CANONICAL
    )
    if out.get("operational_visibility"):
        out["visibility"] = out["operational_visibility"]

    mode = str(out.get("allocation_mode") or "FIXED_AMOUNT").upper()
    if mode not in ALLOCATION_MODES:
        mode = "FIXED_AMOUNT"
    out["allocation_mode"] = mode

    out["monthly_budget_minor"] = _as_minor(out.get("monthly_budget_minor"))
    out["approval_threshold_minor"] = _as_minor(out.get("approval_threshold_minor"))
    out["allow_overallocation"] = _as_bool(out.get("allow_overallocation"))
    out["allow_multi_currency"] = _as_bool(out.get("allow_multi_currency"))

    for flag in (
        "approval_required_for_spend",
        "approval_required_for_vendor_changes",
        "approval_required_for_budget_changes",
        "approval_required_for_issue_closure",
        "invite_on_activation",
        "notify_members",
        "activate_monitoring",
        "confirm_budget",
        "confirm_allocations",
        "confirm_governance",
        "confirm_members",
        "confirm_alerts",
    ):
        if flag in out:
            out[flag] = _as_bool(out.get(flag))

    cats = out.get("budget_categories")
    if isinstance(cats, str):
        out["budget_categories"] = [cats]
    elif cats is None:
        out["budget_categories"] = []

    raw_alloc = out.get("budget_allocations") or []
    if not isinstance(raw_alloc, list):
        raw_alloc = []
    out["budget_allocations"] = resolve_allocations(
        monthly_budget_minor=out.get("monthly_budget_minor"),
        allocations=raw_alloc,
        allocation_mode=mode,
    )

    for list_key in ("secondary_approver_ids", "alert_recipient_ids"):
        val = out.get(list_key)
        if isinstance(val, str):
            text = val.strip()
            if text.startswith("["):
                # Keep as-is for JSON array strings if already parsed elsewhere; split CSV otherwise.
                try:
                    import json

                    parsed = json.loads(text)
                    out[list_key] = [str(x) for x in parsed] if isinstance(parsed, list) else [text]
                except Exception:
                    out[list_key] = [p.strip() for p in text.split(",") if p.strip()]
            elif "," in text:
                out[list_key] = [p.strip() for p in text.split(",") if p.strip()]
            elif text:
                out[list_key] = [text]
            else:
                out[list_key] = []
        elif val is None:
            out[list_key] = []
        elif isinstance(val, list):
            out[list_key] = [str(x) for x in val]

    members_raw = out.get("members") or out.get("member_drafts") or []
    members = [
        normalize_member(m, owner_user_id=owner_user_id)
        for m in members_raw
        if isinstance(m, dict)
    ]
    if owner_user_id:
        members = inject_owner_member(
            members, owner_user_id, owner_display_name=owner_display_name
        )
        out["operations_owner_id"] = str(owner_user_id)
    out["members"] = dedupe_members(members)
    out.pop("member_drafts", None)

    member_ids: set[str] = set()
    owner_value: str | None = None
    for m in out["members"]:
        if m.get("local_id"):
            member_ids.add(str(m["local_id"]))
        if m.get("user_id"):
            member_ids.add(str(m["user_id"]))
        if str(m.get("role") or "").upper() == "OWNER" and owner_value is None:
            owner_value = str(m.get("user_id") or m.get("local_id") or "") or None

    needs_owner = str(out.get("approval_model") or "NONE").upper() in {
        "OWNER_ONLY",
        "SINGLE_APPROVER",
        "MULTI_APPROVER",
        "THRESHOLD_BASED",
        "ROLE_BASED",
    }
    if needs_owner and owner_value:
        current = out.get("approval_owner_id")
        if not current or str(current) not in member_ids:
            out["approval_owner_id"] = owner_value
    if owner_value:
        escalation = out.get("escalation_contact_id")
        if not escalation or str(escalation) not in member_ids:
            out["escalation_contact_id"] = owner_value

    roles = out.get("supported_roles")
    if not isinstance(roles, list) or not roles:
        out["supported_roles"] = list(SUPPORTED_ROLES_V1)
    else:
        out["supported_roles"] = [str(r).upper() for r in roles]

    return out
