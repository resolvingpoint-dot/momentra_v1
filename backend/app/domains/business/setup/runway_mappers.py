"""Business Runway answer/member normalizers (canonical contract values)."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

from app.domains.business.setup.normalizers import normalize_answers as shared_field_aliases
from app.domains.business.setup.runway_permissions import (
    PERMISSION_VERSION_V1,
    SUPPORTED_ROLES_V1,
    default_profile_for_role,
)

BUSINESS_STAGE_CANONICAL = {
    "IDEA",
    "PRE_REVENUE",
    "EARLY_REVENUE",
    "GROWTH",
    "MATURE",
    "TURNAROUND",
    "CUSTOM",
}
_STAGE_ALIASES = {
    "idea": "IDEA",
    "mvp": "PRE_REVENUE",
    "pre_revenue": "PRE_REVENUE",
    "early_revenue": "EARLY_REVENUE",
    "growth": "GROWTH",
    "smb": "MATURE",
    "mature": "MATURE",
    "turnaround": "TURNAROUND",
    "custom": "CUSTOM",
}

REVENUE_STATUS_CANONICAL = {
    "NO_REVENUE",
    "EARLY_REVENUE",
    "RECURRING_REVENUE",
    "VARIABLE_REVENUE",
    "PROFITABLE",
    "CUSTOM",
}

REVENUE_MODEL_CANONICAL = {
    "SUBSCRIPTION",
    "TRANSACTIONAL",
    "SERVICES",
    "RETAIL",
    "MARKETPLACE",
    "LICENSING",
    "ADVERTISING",
    "MIXED",
    "CUSTOM",
}
# Legacy SQL CHECK values → nearest canonical when needed for column write
_REVENUE_MODEL_TO_SQL = {
    "SUBSCRIPTION": "subscription_revenue",
    "TRANSACTIONAL": "product_sales",
    "SERVICES": "service_revenue",
    "RETAIL": "product_sales",
    "MARKETPLACE": "commission_revenue",
    "LICENSING": "product_sales",
    "ADVERTISING": "service_revenue",
    "MIXED": "mixed",
    "CUSTOM": "custom",
}

FUNDING_SOURCES_CANONICAL = {
    "BOOTSTRAPPED",
    "FOUNDER_CAPITAL",
    "FRIENDS_FAMILY",
    "ANGEL",
    "VC",
    "DEBT",
    "GRANT",
    "REVENUE_FUNDED",
    "OTHER",
}
_FUNDING_TO_SQL = {
    "BOOTSTRAPPED": "owner_funded",
    "FOUNDER_CAPITAL": "owner_funded",
    "FRIENDS_FAMILY": "owner_funded",
    "ANGEL": "investor_funded",
    "VC": "investor_funded",
    "DEBT": "bank_loan",
    "GRANT": "government_grant",
    "REVENUE_FUNDED": "revenue_funded",
    "OTHER": "custom",
}

VISIBILITY_CANONICAL = {"PRIVATE", "TEAM", "LEADERSHIP", "ORGANIZATION"}
_VISIBILITY_ALIASES = {
    "private": "PRIVATE",
    "team": "TEAM",
    "team_only": "TEAM",
    "leadership": "LEADERSHIP",
    "organization": "ORGANIZATION",
    "org": "ORGANIZATION",
    "PRIVATE": "PRIVATE",
    "TEAM": "TEAM",
    "LEADERSHIP": "LEADERSHIP",
    "ORGANIZATION": "ORGANIZATION",
    "ORG": "ORGANIZATION",
}

INVITE_METHODS = {"EMAIL", "SMS", "WHATSAPP", "QR", "SHARE", "COPY_LINK", "NATIVE_SHARE"}

_ZERO_DECIMAL_CURRENCIES = {"JPY", "KRW", "VND"}
_THREE_DECIMAL_CURRENCIES = {"KWD", "BHD", "OMR"}


def currency_exponent(code: str | None) -> int:
    c = (code or "USD").upper()
    if c in _ZERO_DECIMAL_CURRENCIES:
        return 0
    if c in _THREE_DECIMAL_CURRENCIES:
        return 3
    return 2


def minor_to_major(minor: int | None, currency_code: str | None) -> Decimal:
    if minor is None:
        return Decimal("0")
    exp = currency_exponent(currency_code)
    quant = Decimal("1") if exp == 0 else (Decimal("0.1") ** exp)
    return (Decimal(int(minor)) / (Decimal(10) ** exp)).quantize(quant, rounding=ROUND_HALF_UP)


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


def _as_int(value: Any) -> int | None:
    return _as_minor(value)


def normalize_business_stage(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    mapped = _STAGE_ALIASES.get(key.lower()) or _STAGE_ALIASES.get(key.upper().lower())
    if mapped:
        return mapped
    upper = key.upper().replace("-", "_").replace(" ", "_")
    return upper if upper in BUSINESS_STAGE_CANONICAL else None


def normalize_revenue_status(value: Any) -> str | None:
    if value is None or value == "":
        return None
    upper = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    return upper if upper in REVENUE_STATUS_CANONICAL else None


def normalize_revenue_model(value: Any) -> str | None:
    if value is None or value == "":
        return None
    upper = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "PRODUCT_SALES": "RETAIL",
        "SERVICE_REVENUE": "SERVICES",
        "SUBSCRIPTION_REVENUE": "SUBSCRIPTION",
        "PROJECT_REVENUE": "SERVICES",
        "COMMISSION_REVENUE": "MARKETPLACE",
    }
    upper = aliases.get(upper, upper)
    return upper if upper in REVENUE_MODEL_CANONICAL else None


def revenue_model_to_sql(canonical: str | None) -> str:
    if not canonical:
        return "custom"
    return _REVENUE_MODEL_TO_SQL.get(canonical.upper(), "custom")


def normalize_funding_source(value: Any) -> str | None:
    if value is None or value == "":
        return None
    upper = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "OWNER_FUNDED": "BOOTSTRAPPED",
        "INVESTOR_FUNDED": "VC",
        "BANK_LOAN": "DEBT",
        "CREDIT_LINE": "DEBT",
        "GOVERNMENT_GRANT": "GRANT",
    }
    upper = aliases.get(upper, upper)
    return upper if upper in FUNDING_SOURCES_CANONICAL else None


def funding_sources_to_sql_primary(sources: list[str] | None) -> str:
    if not sources:
        return "custom"
    first = sources[0].upper()
    return _FUNDING_TO_SQL.get(first, "custom")


def normalize_visibility(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = str(value).strip()
    return _VISIBILITY_ALIASES.get(key) or _VISIBILITY_ALIASES.get(key.upper())


def normalize_member(raw: dict[str, Any], *, owner_user_id: str | None = None) -> dict[str, Any]:
    role = str(raw.get("role") or "CONTRIBUTOR").upper()
    if role not in SUPPORTED_ROLES_V1:
        role = "CONTRIBUTOR"
    is_owner = role == "OWNER" and owner_user_id and str(raw.get("user_id") or "") == str(owner_user_id)
    invite_method = str(raw.get("invite_method") or "EMAIL").upper()
    if invite_method not in INVITE_METHODS:
        invite_method = "EMAIL"
    profile = raw.get("permission_profile") or default_profile_for_role(role)
    return {
        "local_id": str(raw.get("local_id") or uuid4()),
        "user_id": str(raw["user_id"]) if raw.get("user_id") else None,
        "name": str(raw.get("name") or role),
        "email": (str(raw["email"]).strip() if raw.get("email") else None),
        "phone": (str(raw["phone"]).strip() if raw.get("phone") else None),
        "role": role,
        "permission_profile": profile,
        "permission_version": int(raw.get("permission_version") or PERMISSION_VERSION_V1),
        "invite_method": invite_method,
        "invite_status": "ACCEPTED" if is_owner or role == "OWNER" and owner_user_id and str(raw.get("user_id")) == str(owner_user_id) else str(raw.get("invite_status") or "DRAFT").upper(),
        "is_finance_lead": _as_bool(raw.get("is_finance_lead")) or role == "FINANCE_LEAD",
        "is_operations_lead": _as_bool(raw.get("is_operations_lead")) or role == "OPERATIONS_LEAD",
        "is_advisor": _as_bool(raw.get("is_advisor")) or role == "ADVISOR",
        "is_observer": _as_bool(raw.get("is_observer")) or role == "OBSERVER",
    }


def inject_owner_member(
    members: list[dict[str, Any]],
    owner_user_id: str,
    *,
    owner_display_name: str | None = None,
) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for m in members:
        if str(m.get("user_id") or "") == str(owner_user_id) or m.get("role") == "OWNER":
            continue
        cleaned.append(m)
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
        "is_finance_lead": False,
        "is_operations_lead": False,
        "is_advisor": False,
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


def normalize_runway_answers(
    answers: dict[str, Any] | None,
    *,
    owner_user_id: str | None = None,
    owner_display_name: str | None = None,
) -> dict[str, Any]:
    raw = shared_field_aliases(answers)
    # Legacy key aliases
    if "cash_available_minor" in raw and "current_cash_minor" not in raw:
        raw["current_cash_minor"] = raw.pop("cash_available_minor")
    if "runway_goal" in raw and "runway_goal_months" not in raw:
        # Do not coerce goal-type enums into months — ignore non-int
        maybe = _as_int(raw.get("runway_goal"))
        if maybe is not None:
            raw["runway_goal_months"] = maybe

    out = dict(raw)
    out["business_stage"] = normalize_business_stage(out.get("business_stage"))
    out["revenue_status"] = normalize_revenue_status(out.get("revenue_status"))
    out["revenue_model"] = normalize_revenue_model(out.get("revenue_model"))
    out["visibility"] = normalize_visibility(out.get("visibility"))

    currency = (
        out.get("operating_currency_code")
        or out.get("default_currency_code")
        or out.get("currency")
    )
    if currency:
        out["operating_currency_code"] = str(currency).upper()

    for key in (
        "current_cash_minor",
        "monthly_burn_minor",
        "estimated_monthly_revenue_minor",
        "large_expense_threshold_minor",
    ):
        if key in out:
            out[key] = _as_minor(out.get(key))

    for key in ("runway_goal_months", "runway_alert_threshold_months", "collection_rate_percent"):
        if key in out:
            out[key] = _as_int(out.get(key))

    if out.get("collection_rate_percent") is not None:
        pct = int(out["collection_rate_percent"])
        out["collection_rate_percent"] = max(0, min(100, pct))

    funding = out.get("funding_sources")
    if isinstance(funding, str):
        funding = [funding]
    if isinstance(funding, list):
        out["funding_sources"] = [
            s for s in (normalize_funding_source(x) for x in funding) if s
        ]

    burn = out.get("burn_categories")
    if isinstance(burn, str):
        out["burn_categories"] = [burn]
    elif burn is None:
        out["burn_categories"] = []

    for flag in (
        "allow_multi_currency",
        "approval_required_for_funding_changes",
        "approval_required_for_cash_adjustments",
        "approval_required_for_large_expenses",
        "approval_required_for_threshold_changes",
        "invite_on_activation",
        "notify_members",
        "confirm_financial_inputs",
        "confirm_governance",
    ):
        if flag in out:
            out[flag] = _as_bool(out.get(flag))

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
        out["runway_owner_id"] = str(owner_user_id)
    members = dedupe_members(members)
    out["members"] = members
    if "member_drafts" in out:
        del out["member_drafts"]

    # Default approval owner when any approval flag is on (web/mobile parity).
    approvals_on = any(
        bool(out.get(flag))
        for flag in (
            "approval_required_for_funding_changes",
            "approval_required_for_cash_adjustments",
            "approval_required_for_large_expenses",
            "approval_required_for_threshold_changes",
        )
    )
    if approvals_on:
        member_ids: set[str] = set()
        owner_value: str | None = None
        for m in members:
            if m.get("local_id"):
                member_ids.add(str(m["local_id"]))
            if m.get("user_id"):
                member_ids.add(str(m["user_id"]))
            if str(m.get("role") or "").upper() == "OWNER" and owner_value is None:
                owner_value = str(m.get("user_id") or m.get("local_id") or "") or None
        current = out.get("approval_owner_id")
        if not current or str(current) not in member_ids:
            if owner_value:
                out["approval_owner_id"] = owner_value

    roles = out.get("supported_roles")
    if not isinstance(roles, list) or not roles:
        out["supported_roles"] = list(SUPPORTED_ROLES_V1)
    else:
        out["supported_roles"] = [str(r).upper() for r in roles]

    return out


def compute_derived_preview(answers: dict[str, Any]) -> dict[str, Any]:
    cash = _as_minor(answers.get("current_cash_minor"))
    burn = _as_minor(answers.get("monthly_burn_minor"))
    revenue = _as_minor(answers.get("estimated_monthly_revenue_minor")) or 0
    goal = _as_int(answers.get("runway_goal_months"))

    estimated = None
    if cash is not None and burn is not None and burn > 0:
        estimated = cash // burn

    net = None
    if burn is not None:
        net = burn - revenue

    gap = None
    if estimated is not None and goal is not None:
        gap = goal - estimated

    return {
        "estimated_runway_months": estimated,
        "net_monthly_burn_minor": net,
        "goal_gap_months": gap,
    }
