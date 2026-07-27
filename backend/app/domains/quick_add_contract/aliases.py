"""Canonical Quick Add v1 aliases — normalize once at the boundary."""
from __future__ import annotations

MOMENT_TYPE_ALIASES: dict[str, str] = {
    "TRIP": "SHARED_EXPERIENCE",
    "EMOTIONAL_SECURITY": "RELATIONSHIPS",
}

# UI / legacy action ids → canonical action_id (context-sensitive where noted).
ACTION_ID_ALIASES: dict[str, str] = {
    "RENT": "EXPENSE",
    "UTILITY": "EXPENSE",
    "CAPTURE_MEMORY": "MEMORY",
    "HOME_MEMORY": "MEMORY",
    "PURCHASE_EXPENSE": "EXPENSE",
    "RELATIONSHIP_ADJUST": "ADJUST",
}

# Reserved for a future money-contribution write path on SHARED_PURCHASE.
# Must NEVER alias to CONTRIBUTOR (people) or CONTRIBUTION (ambiguous).
RESERVED_ACTION_IDS: frozenset[str] = frozenset({"PURCHASE_CONTRIBUTION"})

PAYER_FIELD_ALIASES: tuple[str, ...] = (
    "paid_by_participant_id",
    "paid_by",
    "paidBy",
    "payer",
    "paid_by_user_id",
    "paid_by_member_id",
    "paid_by_member",
)

AMOUNT_FIELD_ALIASES: tuple[str, ...] = (
    "amount_minor",
    "amount",
    "amount_major",
)

CURRENCY_FIELD_ALIASES: tuple[str, ...] = (
    "currency_code",
    "currency",
    "currencyCode",
)

CATEGORY_FIELD_ALIASES: tuple[str, ...] = (
    "category_code",
    "category",
    "expense_category",
    "category_name",
)

SUBCATEGORY_FIELD_ALIASES: tuple[str, ...] = (
    "subcategory_code",
    "subcategory",
    "sub_category",
    "expense_subcategory",
)


def normalize_moment_type_code(code: str | None) -> str:
    if not code:
        return ""
    raw = str(code).strip()
    return MOMENT_TYPE_ALIASES.get(raw, raw)


def normalize_action_id(action_id: str | None, *, moment_type_code: str | None = None) -> str:
    if not action_id:
        return ""
    raw = str(action_id).strip().upper()
    # Preserve people CONTRIBUTOR; do not collapse to money CONTRIBUTION / PURCHASE_CONTRIBUTION.
    if raw == "CONTRIBUTOR":
        return "CONTRIBUTOR"
    if raw in RESERVED_ACTION_IDS:
        return raw
    canonical = ACTION_ID_ALIASES.get(raw, raw)
    _ = moment_type_code  # reserved for context-specific overrides
    return canonical


def rent_category_for_alias(action_id: str | None) -> str | None:
    raw = str(action_id or "").strip().upper()
    if raw == "RENT":
        return "rent"
    if raw == "UTILITY":
        return "utility"
    return None
