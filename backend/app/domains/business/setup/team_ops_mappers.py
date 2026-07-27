"""Team Operations answer/member normalizers and safe enum aliases."""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.domains.business.setup.normalizers import normalize_answers as shared_field_aliases
from app.domains.business.setup.team_ops_permissions import (
    PERMISSION_VERSION_V1,
    SUPPORTED_ROLES_V1,
    default_profile_for_role,
)

# Size bands — legacy ↔ canonical (equivalent meaning).
TEAM_SIZE_CANONICAL = {"SOLO", "SMALL", "MEDIUM", "LARGE", "XLARGE"}
_TEAM_SIZE_FROM_LEGACY = {
    "just_me": "SOLO",
    "2_5": "SMALL",
    "6_15": "MEDIUM",
    "16_50": "LARGE",
    "50_plus": "XLARGE",
    "SOLO": "SOLO",
    "SMALL": "SMALL",
    "MEDIUM": "MEDIUM",
    "LARGE": "LARGE",
    "XLARGE": "XLARGE",
}
_TEAM_SIZE_TO_LEGACY = {
    "SOLO": "just_me",
    "SMALL": "2_5",
    "MEDIUM": "6_15",
    "LARGE": "16_50",
    "XLARGE": "50_plus",
}

WORK_STYLE_CANONICAL = {"REMOTE", "HYBRID", "IN_PERSON"}
VISIBILITY_CANONICAL = {"PRIVATE", "TEAM", "ORG"}
_VISIBILITY_FROM_LEGACY = {
    "team_only": "TEAM",
    "leadership": "PRIVATE",  # leadership-gated ≈ private-to-leads; store canonical PRIVATE/TEAM/ORG in extras
    "organization": "ORG",
    "private": "PRIVATE",
    "PRIVATE": "PRIVATE",
    "TEAM": "TEAM",
    "ORG": "ORG",
}
_VISIBILITY_TO_LEGACY_SETUP = {
    "PRIVATE": "leadership",
    "TEAM": "team_only",
    "ORG": "organization",
}

COORDINATION_CANONICAL = {
    "INDEPENDENT",
    "CROSS_FUNCTIONAL",
    "LEADERSHIP_DRIVEN",
    "SHARED_OWNERSHIP",
}
_COORDINATION_FROM_LEGACY = {
    "independent": "INDEPENDENT",
    "cross_functional": "CROSS_FUNCTIONAL",
    "leadership_driven": "LEADERSHIP_DRIVEN",
    "shared_ownership": "SHARED_OWNERSHIP",
}
_COORDINATION_TO_LEGACY = {v: k for k, v in _COORDINATION_FROM_LEGACY.items()}

MONITORING_CANONICAL = {"BASIC", "STANDARD", "HIGH_VISIBILITY"}
_MONITORING_FROM_LEGACY = {
    "basic": "BASIC",
    "standard": "STANDARD",
    "high_visibility": "HIGH_VISIBILITY",
}
_MONITORING_TO_LEGACY = {v: k for k, v in _MONITORING_FROM_LEGACY.items()}

REVIEW_CYCLE_CANONICAL = {"WEEKLY", "BIWEEKLY", "MONTHLY", "QUARTERLY"}

INVITE_METHODS = {"EMAIL", "SMS", "WHATSAPP", "QR", "SHARE", "COPY_LINK", "NATIVE_SHARE"}


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
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n


def normalize_team_size(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    return _TEAM_SIZE_FROM_LEGACY.get(key) or _TEAM_SIZE_FROM_LEGACY.get(key.upper()) or (
        key.upper() if key.upper() in TEAM_SIZE_CANONICAL else None
    )


def team_size_to_legacy(canonical: str | None) -> str | None:
    if not canonical:
        return None
    return _TEAM_SIZE_TO_LEGACY.get(canonical.upper())


def normalize_work_style(value: Any) -> str | None:
    """Canonical work_style only — do not coerce from legacy planned/mixed/fast_response."""
    if value is None or value == "":
        return None
    key = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    if key in {"INPERSON", "IN_PERSON", "ONSITE", "ON_SITE"}:
        key = "IN_PERSON"
    return key if key in WORK_STYLE_CANONICAL else None


def normalize_visibility(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    mapped = _VISIBILITY_FROM_LEGACY.get(key) or _VISIBILITY_FROM_LEGACY.get(key.upper())
    return mapped if mapped in VISIBILITY_CANONICAL else None


def visibility_to_legacy_setup(canonical: str | None) -> str | None:
    if not canonical:
        return None
    return _VISIBILITY_TO_LEGACY_SETUP.get(canonical.upper())


def normalize_coordination(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    mapped = _COORDINATION_FROM_LEGACY.get(key.lower()) or key.upper()
    return mapped if mapped in COORDINATION_CANONICAL else None


def coordination_to_legacy(canonical: str | None) -> str | None:
    if not canonical:
        return None
    return _COORDINATION_TO_LEGACY.get(canonical.upper())


def normalize_monitoring(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    mapped = _MONITORING_FROM_LEGACY.get(key.lower()) or key.upper()
    return mapped if mapped in MONITORING_CANONICAL else None


def monitoring_to_legacy(canonical: str | None) -> str | None:
    if not canonical:
        return None
    return _MONITORING_TO_LEGACY.get(canonical.upper())


def normalize_review_cycle(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip().upper()
    return key if key in REVIEW_CYCLE_CANONICAL else None


def _normalize_member(raw: Any, *, owner_user_id: str | None = None) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    role = str(raw.get("role") or "MEMBER").strip().upper()
    if role not in SUPPORTED_ROLES_V1:
        role = "MEMBER"
    profile = raw.get("permission_profile") or default_profile_for_role(role)
    profile = str(profile)
    if not profile.endswith("_V1") and profile.upper() in ROLE_TO_PROFILE_SAFE:
        profile = ROLE_TO_PROFILE_SAFE[profile.upper()]
    local_id = str(raw.get("local_id") or uuid4())
    invite_method = (str(raw.get("invite_method") or "EMAIL")).strip().upper()
    if invite_method not in INVITE_METHODS:
        invite_method = "EMAIL"
    invite_status = (str(raw.get("invite_status") or "DRAFT")).strip().upper()
    user_id = raw.get("user_id")
    if user_id is not None:
        user_id = str(user_id)
    name = raw.get("name")
    if name is not None:
        name = str(name).strip() or None
    email = raw.get("email")
    if email is not None:
        email = str(email).strip().lower() or None
    phone = raw.get("phone")
    if phone is not None:
        phone = str(phone).strip() or None
    return {
        "local_id": local_id,
        "user_id": user_id,
        "name": name or ("Owner" if role == "OWNER" else ""),
        "email": email,
        "phone": phone,
        "role": role,
        "permission_profile": profile if str(profile).endswith("_V1") else default_profile_for_role(role),
        "permission_version": int(raw.get("permission_version") or PERMISSION_VERSION_V1),
        "invite_method": invite_method,
        "invite_status": invite_status,
        "is_approver": _as_bool(raw.get("is_approver"), role == "APPROVER"),
        "is_budget_owner": _as_bool(raw.get("is_budget_owner"), role in {"BUDGET_OWNER", "FINANCE_LEAD"}),
    }


# Avoid circular import of ROLE map detail
ROLE_TO_PROFILE_SAFE = {
    "OWNER": "OWNER_V1",
    "ADMIN": "ADMIN_V1",
    "TEAM_LEAD": "TEAM_LEAD_V1",
    "OPERATIONS_LEAD": "OPERATIONS_LEAD_V1",
    "FINANCE_LEAD": "FINANCE_LEAD_V1",
    "BUDGET_OWNER": "BUDGET_OWNER_V1",
    "APPROVER": "APPROVER_V1",
    "CONTRIBUTOR": "CONTRIBUTOR_V1",
    "MEMBER": "TEAM_MEMBER_V1",
    "OBSERVER": "OBSERVER_V1",
}


def _dedupe_members(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_email: set[str] = set()
    seen_phone: set[str] = set()
    out: list[dict[str, Any]] = []
    for m in members:
        email = (m.get("email") or "").lower()
        phone = m.get("phone") or ""
        if email and email in seen_email:
            continue
        if phone and phone in seen_phone:
            continue
        if email:
            seen_email.add(email)
        if phone:
            seen_phone.add(phone)
        out.append(m)
    return out


def inject_owner_member(
    members: list[dict[str, Any]],
    owner_user_id: str,
    *,
    owner_display_name: str | None = None,
) -> list[dict[str, Any]]:
    """Ensure auth owner is present, locked OWNER, and cannot be replaced."""
    owner_id = str(owner_user_id)
    display = (owner_display_name or "").strip() or "You"
    others: list[dict[str, Any]] = []
    owner_row: dict[str, Any] | None = None
    for m in members:
        uid = str(m.get("user_id") or "")
        if uid == owner_id:
            owner_row = dict(m)
            continue
        if (m.get("role") or "").upper() == "OWNER":
            demoted = dict(m)
            demoted["role"] = "MEMBER"
            demoted["permission_profile"] = "TEAM_MEMBER_V1"
            others.append(demoted)
            continue
        others.append(m)

    if owner_row is None:
        owner_row = {
            "local_id": f"owner-{owner_id}",
            "user_id": owner_id,
            "name": display,
            "email": None,
            "phone": None,
            "role": "OWNER",
            "permission_profile": "OWNER_V1",
            "permission_version": PERMISSION_VERSION_V1,
            "invite_method": "SHARE",
            "invite_status": "ACCEPTED",
            "is_approver": True,
            "is_budget_owner": True,
        }
    else:
        owner_row["user_id"] = owner_id
        owner_row["role"] = "OWNER"
        owner_row["permission_profile"] = "OWNER_V1"
        owner_row["permission_version"] = PERMISSION_VERSION_V1
        owner_row["invite_status"] = "ACCEPTED"
        owner_row["is_approver"] = True
        owner_row["is_budget_owner"] = True
        if not owner_row.get("local_id"):
            owner_row["local_id"] = f"owner-{owner_id}"
        existing_name = str(owner_row.get("name") or "").strip()
        if not existing_name or existing_name in {"Team owner", "Owner"}:
            owner_row["name"] = display

    return [owner_row, *others]


def normalize_team_ops_answers(
    answers: dict[str, Any] | None,
    *,
    owner_user_id: str | None = None,
    owner_display_name: str | None = None,
) -> dict[str, Any]:
    out = shared_field_aliases(answers)
    # Currency / operating currency collapse.
    currency = (
        out.get("operating_currency_code")
        or out.get("default_currency_code")
        or out.pop("currency", None)
        or out.pop("currency_code", None)
        or out.pop("operating_currency", None)
    )
    if currency is not None:
        code = str(currency).strip().upper() or None
        out["operating_currency_code"] = code
        out["default_currency_code"] = code

    if "team_size" in out:
        out["team_size"] = normalize_team_size(out.get("team_size"))
    if "work_style" in out:
        # Drop invalid / legacy non-equivalent values rather than remapping.
        ws = normalize_work_style(out.get("work_style"))
        if ws is None and out.get("work_style") is not None:
            # Preserve unknown key under extras-style only if already canonical missed
            legacy = str(out.get("work_style")).strip().lower()
            if legacy in {"planned", "mixed", "fast_response"}:
                out.pop("work_style", None)  # refuse false mapping
            else:
                out["work_style"] = None
        else:
            out["work_style"] = ws
    if "visibility" in out:
        out["visibility"] = normalize_visibility(out.get("visibility"))
    if "coordination_style" in out:
        out["coordination_style"] = normalize_coordination(out.get("coordination_style"))
    if "monitoring_level" in out:
        out["monitoring_level"] = normalize_monitoring(out.get("monitoring_level"))
    if "review_cycle" in out:
        out["review_cycle"] = normalize_review_cycle(out.get("review_cycle"))

    for key in ("monthly_team_budget_minor", "approval_threshold_minor"):
        if key in out:
            out[key] = _as_minor(out.get(key))

    for key in (
        "allow_multi_currency",
        "approval_required_for_spend",
        "approval_required_for_member_changes",
        "invite_on_activation",
        "notify_members",
        "confirm_owner",
        "confirm_permissions",
        "confirm_governance",
    ):
        if key in out:
            out[key] = _as_bool(out.get(key))

    # Members: merge legacy member_drafts into members.
    raw_members = out.get("members")
    if not isinstance(raw_members, list):
        raw_members = []
    legacy = out.pop("member_drafts", None)
    if isinstance(legacy, list):
        raw_members = [*raw_members, *legacy]

    members: list[dict[str, Any]] = []
    for item in raw_members:
        normalized = _normalize_member(item, owner_user_id=owner_user_id)
        if normalized:
            members.append(normalized)
    members = _dedupe_members(members)
    if owner_user_id:
        members = inject_owner_member(
            members, owner_user_id, owner_display_name=owner_display_name
        )
        out["team_owner_id"] = str(owner_user_id)
    out["members"] = members
    out["member_drafts"] = members  # keep alias for older clients

    roles = out.get("supported_roles")
    if isinstance(roles, list):
        cleaned = []
        for r in roles:
            rr = str(r).strip().upper()
            if rr in SUPPORTED_ROLES_V1 and rr not in cleaned:
                cleaned.append(rr)
        if "OWNER" not in cleaned:
            cleaned.insert(0, "OWNER")
        out["supported_roles"] = cleaned
    elif owner_user_id and "supported_roles" not in out:
        out["supported_roles"] = list(SUPPORTED_ROLES_V1)

    return out
