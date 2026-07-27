"""Payload normalization for Quick Add v1 wire shape."""
from __future__ import annotations

from typing import Any, Mapping

from app.domains.quick_add_contract.aliases import (
    AMOUNT_FIELD_ALIASES,
    CATEGORY_FIELD_ALIASES,
    CURRENCY_FIELD_ALIASES,
    PAYER_FIELD_ALIASES,
    SUBCATEGORY_FIELD_ALIASES,
    normalize_action_id,
    normalize_moment_type_code,
    rent_category_for_alias,
)
from app.domains.reference_data.expense_taxonomy import (
    LEGACY_LIVING_CATEGORY_CODES,
    normalize_expense_category_code,
)


def _first_present(data: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data and data[key] is not None and data[key] != "":
            return data[key]
    return None


def _to_amount_minor(value: Any, *, from_major_key: bool = False) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if not from_major_key else value * 100
    try:
        raw = str(value).replace(",", "").strip()
        if not raw:
            return None
        if "." in raw or from_major_key:
            return int(round(float(raw) * (1 if not from_major_key and "." not in raw else 100 if from_major_key or "." in raw else 1)))
        return int(raw)
    except (TypeError, ValueError):
        return None


def normalize_payload(
    data: Mapping[str, Any] | None,
    *,
    moment_type_code: str | None = None,
    action_id: str | None = None,
) -> dict[str, Any]:
    """Collapse aliases to canonical v1 field names. Does not mutate input."""
    src = dict(data or {})
    out: dict[str, Any] = dict(src)

    mt = normalize_moment_type_code(moment_type_code or src.get("moment_type_code"))
    if mt:
        out["moment_type_code"] = mt

    raw_action = action_id or src.get("action_id") or src.get("event_type")
    rent_cat = rent_category_for_alias(str(raw_action) if raw_action else None)
    canonical_action = normalize_action_id(
        str(raw_action) if raw_action else None,
        moment_type_code=mt,
    )
    if canonical_action:
        out["action_id"] = canonical_action
        if "event_type" in src or action_id:
            out["event_type"] = canonical_action

    payer = _first_present(src, PAYER_FIELD_ALIASES)
    if payer is not None:
        out["paid_by_participant_id"] = str(payer)
        for alias in PAYER_FIELD_ALIASES:
            if alias != "paid_by_participant_id":
                out.pop(alias, None)

    # amount_minor: prefer explicit; else amount (major decimal string); else amount_major
    if "amount_minor" in src and src["amount_minor"] not in (None, ""):
        try:
            out["amount_minor"] = int(src["amount_minor"])
        except (TypeError, ValueError):
            out["amount_minor"] = _to_amount_minor(src["amount_minor"]) or 0
    elif "amount_major" in src and src["amount_major"] not in (None, ""):
        out["amount_minor"] = _to_amount_minor(src["amount_major"], from_major_key=True) or 0
        out.pop("amount_major", None)
    elif "amount" in src and src["amount"] not in (None, ""):
        out["amount_minor"] = _to_amount_minor(src["amount"], from_major_key=True) or 0
        out.pop("amount", None)

    currency = _first_present(src, CURRENCY_FIELD_ALIASES)
    if currency is not None:
        out["currency_code"] = str(currency).upper().strip()
        for alias in CURRENCY_FIELD_ALIASES:
            if alias != "currency_code":
                out.pop(alias, None)

    category = _first_present(src, CATEGORY_FIELD_ALIASES)
    if rent_cat:
        out["category_code"] = rent_cat
        out["subcategory_code"] = None
    elif category is not None:
        out["category_code"] = normalize_expense_category_code(str(category))
    for alias in CATEGORY_FIELD_ALIASES:
        if alias != "category_code":
            out.pop(alias, None)

    # Explicit null clears subcategory; empty aliases ignored.
    if "subcategory_code" in src and src.get("subcategory_code") is None:
        out["subcategory_code"] = None
    else:
        raw_sub = _first_present(src, SUBCATEGORY_FIELD_ALIASES)
        if raw_sub is not None:
            cat_for_sub = str(out.get("category_code") or "")
            if cat_for_sub.lower() in LEGACY_LIVING_CATEGORY_CODES:
                out["subcategory_code"] = None
            else:
                out["subcategory_code"] = normalize_expense_category_code(str(raw_sub))
    for alias in SUBCATEGORY_FIELD_ALIASES:
        if alias != "subcategory_code":
            out.pop(alias, None)

    if "split_type" in out and "split_style" not in out:
        out["split_style"] = str(out.pop("split_type")).upper()
    elif "split_style" in out:
        out["split_style"] = str(out["split_style"]).upper()

    # Nested personal expense block
    expense = out.get("expense")
    if isinstance(expense, dict):
        nested = normalize_payload(expense, moment_type_code=mt, action_id=canonical_action or "EXPENSE")
        out["expense"] = {
            k: nested[k]
            for k in (
                "amount_minor",
                "currency_code",
                "account_id",
                "category_code",
                "subcategory_code",
                "transaction_type",
                "pressure_impact",
            )
            if k in nested
        }
        for k in ("amount_minor", "currency_code", "account_id", "category_code", "subcategory_code"):
            if k in nested and k not in out:
                out[k] = nested[k]

    # Contract V2 when subcategory is present (or explicitly cleared); otherwise V1-compatible.
    if "subcategory_code" in out or any(a in src for a in SUBCATEGORY_FIELD_ALIASES):
        out["contract_version"] = "v2"
    else:
        out["contract_version"] = "v1"
    return out
