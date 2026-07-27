"""Canonical Shared Experience / trip expense write contract helpers."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from fastapi import HTTPException, status

from app.domains.group.settlements import calculator
from app.domains.reference_data.constants import CURRENCIES

_SPLIT_ALIASES = {
    "EQUAL": "EQUAL",
    "EQUAL_SPLIT": "EQUAL",
    "EXACT": "EXACT",
    "CUSTOM": "EXACT",
    "CUSTOM_AMOUNT": "EXACT",
    "PERCENTAGE": "PERCENTAGE",
    "PERCENT": "PERCENTAGE",
    "CUSTOM_PERCENTAGE": "PERCENTAGE",
    "SHARES": "SHARES",
    "BY_SHARES": "SHARES",
}


def active_currencies() -> list[dict[str, Any]]:
    return [c for c in CURRENCIES if c.get("is_active", True)]


def currency_codes() -> set[str]:
    return {str(c["code"]).upper() for c in active_currencies()}


def currency_meta(code: str) -> dict[str, Any] | None:
    needle = str(code or "").upper()
    for row in active_currencies():
        if str(row.get("code") or "").upper() == needle:
            return row
    return None


def allow_multi_currency(payload: Mapping[str, Any] | None) -> bool:
    """Legacy absent → True for Experience/group expenses."""
    if not payload or "allow_multi_currency" not in payload:
        return True
    return bool(payload.get("allow_multi_currency"))


def resolve_group_default_currency(
    payload: Mapping[str, Any] | None,
    *,
    user_default: str | None = None,
) -> str:
    payload = payload or {}
    for candidate in (
        payload.get("currency_code"),
        payload.get("budget_currency"),
        user_default,
    ):
        code = str(candidate or "").upper().strip()
        if code and code in currency_codes():
            return code
    # Reference-data default (first active by sort_order) then INR.
    catalog = sorted(active_currencies(), key=lambda c: int(c.get("sort_order") or 0))
    if catalog:
        return str(catalog[0]["code"]).upper()
    return "INR"


def resolve_default_payer(
    members: Sequence[Mapping[str, Any]],
    current_user_id: str | None,
) -> str | None:
    """Priority: current accepted user → ORGANIZER → first accepted (stable) → None."""
    accepted = [m for m in members if str(m.get("id") or "")]
    if not accepted:
        return None
    uid = str(current_user_id or "")
    if uid:
        for m in accepted:
            if str(m.get("user_id") or m.get("id") or "") == uid:
                return str(m.get("id"))
    organizers = [
        m
        for m in accepted
        if str(m.get("role_code") or "").upper() == "ORGANIZER"
    ]
    if organizers:
        organizers.sort(key=lambda m: (str(m.get("created_at") or ""), str(m.get("id") or "")))
        return str(organizers[0].get("id"))
    ordered = sorted(
        accepted,
        key=lambda m: (str(m.get("created_at") or ""), str(m.get("id") or "")),
    )
    return str(ordered[0].get("id"))


def normalize_split_style(raw: Any) -> str:
    text = str(raw or "EQUAL").strip().upper()
    if text.lower() == "equal":
        return "EQUAL"
    return _SPLIT_ALIASES.get(text, calculator.normalize_split_style({"split_type": raw}))


def _split_rows_from_details(
    split_style: str,
    participant_ids: list[str],
    split_details: Any,
) -> list[dict[str, Any]] | None:
    if split_details is None:
        return None
    if isinstance(split_details, list):
        return [dict(row) for row in split_details if isinstance(row, Mapping)]
    if not isinstance(split_details, Mapping):
        return None
    rows: list[dict[str, Any]] = []
    for pid in participant_ids:
        if pid not in split_details and str(pid) not in split_details:
            continue
        val = split_details.get(pid, split_details.get(str(pid)))
        if isinstance(val, Mapping):
            row = {"member_id": pid, **dict(val)}
        elif split_style == "PERCENTAGE":
            row = {"member_id": pid, "percent": int(val or 0)}
        elif split_style == "SHARES":
            row = {"member_id": pid, "shares": int(val or 0)}
        else:
            row = {"member_id": pid, "amount_minor": int(val or 0)}
        rows.append(row)
    return rows or None


def build_resolved_shares(
    *,
    amount_minor: int,
    participant_ids: Sequence[str],
    split_style: str,
    split_details: Any,
) -> list[dict[str, Any]]:
    ids = [str(p) for p in participant_ids if p]
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="participant_ids requires at least one participant",
        )
    splits = _split_rows_from_details(split_style, ids, split_details)
    expense = {
        "amount_minor": amount_minor,
        "split_style": split_style,
        "splits": splits,
    }
    allocated = calculator.allocate_expense(expense, ids)
    total = sum(allocated.values())
    if total != amount_minor:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Resolved shares must sum to amount_minor ({amount_minor}), got {total}",
        )
    return [
        {"member_id": pid, "amount_minor": int(allocated[pid])}
        for pid in sorted(allocated.keys())
    ]


def normalize_expense_write(
    body: Mapping[str, Any],
    *,
    user_id: str,
    members: Sequence[Mapping[str, Any]],
    default_currency: str,
    multi_currency: bool,
    soft_default_participants: bool = True,
    guests: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    title = str(body.get("title") or body.get("description") or "").strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="title is required",
        )
    try:
        amount_minor = int(body.get("amount_minor") or 0)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="amount_minor must be a positive integer",
        ) from exc
    if amount_minor <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="amount_minor must be > 0",
        )

    currency = str(body.get("currency_code") or default_currency or "INR").upper().strip()
    if currency not in currency_codes():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported currency_code: {currency}",
        )
    if not multi_currency and currency != default_currency.upper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Multi-currency is disabled for this group; use the group default currency",
        )

    member_ids = {str(m.get("id")) for m in members if m.get("id")}
    guest_ids = {
        str(g.get("id"))
        for g in (guests or [])
        if g.get("id")
    }
    # Expense context exposes guests as payers/participants; accept both.
    allowed_ids = member_ids | guest_ids

    paid_by = str(
        body.get("paid_by_participant_id")
        or body.get("paid_by_member_id")
        or body.get("paid_by_user_id")
        or ""
    ).strip()
    if not paid_by:
        paid_by = resolve_default_payer(members, user_id) or user_id
    if allowed_ids and paid_by not in allowed_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="paid_by_participant_id must be an accepted member or guest",
        )

    raw_participants = body.get("participant_ids") or body.get("participants")
    if isinstance(raw_participants, str):
        participant_ids = [p.strip() for p in raw_participants.split(",") if p.strip()]
    elif isinstance(raw_participants, list) and raw_participants:
        participant_ids = [str(p) for p in raw_participants if p]
    elif soft_default_participants and member_ids:
        participant_ids = sorted(member_ids)
    elif soft_default_participants and paid_by:
        participant_ids = [paid_by]
    else:
        participant_ids = []
    if not participant_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="participant_ids requires at least one participant",
        )
    if allowed_ids:
        # Drop stale/unknown ids (e.g. UI mixed roster) rather than hard-fail when
        # at least one valid participant remains.
        known = [p for p in participant_ids if p in allowed_ids]
        unknown = [p for p in participant_ids if p not in allowed_ids]
        if known:
            participant_ids = known
        elif unknown:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown participant_ids: {', '.join(unknown)}",
            )

    split_style = normalize_split_style(body.get("split_style") or body.get("split_type"))
    split_details = body.get("split_details")
    if split_details is None:
        split_details = body.get("splits")
    shares = build_resolved_shares(
        amount_minor=amount_minor,
        participant_ids=participant_ids,
        split_style=split_style,
        split_details=split_details,
    )

    category = body.get("category_code") or body.get("category")
    raw_sub = (
        body.get("subcategory_code")
        or body.get("subcategory")
        or body.get("sub_category")
        or body.get("expense_subcategory")
    )
    # Explicit null clears subcategory on edit.
    if "subcategory_code" in body and body.get("subcategory_code") is None:
        raw_sub = None

    from app.domains.reference_data.expense_taxonomy import (
        LEGACY_LIVING_CATEGORY_CODES,
        InvalidExpenseSubcategoryError,
        normalize_expense_category_code,
        validate_expense_category_pair,
    )

    cat_norm = normalize_expense_category_code(str(category) if category is not None else None)
    if cat_norm and cat_norm.lower() in LEGACY_LIVING_CATEGORY_CODES:
        category_out = cat_norm
        subcategory_out = None
    else:
        try:
            category_out, subcategory_out = validate_expense_category_pair(
                cat_norm,
                None if raw_sub in ("", None) else str(raw_sub),
            )
        except InvalidExpenseSubcategoryError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": exc.code, "message": exc.message},
            ) from exc

    occurred_at = body.get("occurred_at") or body.get("expense_date")
    notes = body.get("notes")
    client_request_id = body.get("client_request_id")

    return {
        "title": title,
        "description": title,
        "amount_minor": amount_minor,
        "currency_code": currency,
        "category": category_out,
        "category_code": category_out,
        "subcategory_code": subcategory_out,
        "occurred_at": str(occurred_at) if occurred_at else None,
        "expense_date": str(occurred_at) if occurred_at else None,
        "paid_by_participant_id": paid_by,
        "paid_by_user_id": paid_by,
        "participant_ids": participant_ids,
        "split_style": split_style,
        "split_type": split_style.lower(),
        "split_details": split_details if isinstance(split_details, (dict, list)) else None,
        "shares": shares,
        "notes": str(notes) if notes is not None else None,
        "client_request_id": str(client_request_id) if client_request_id else None,
        "is_settled": False,
        "deleted": False,
    }
