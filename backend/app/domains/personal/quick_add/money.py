"""Shared money-event insertion for personal quick-add handlers."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import (
    money_direction,
    parse_amount,
    pressure_score,
)
from app.domains.personal.lifestyle.quick_add.constants import (
    SPEND_CATEGORY_TO_EXPENSE_CODE,
)
from app.domains.personal.models import PersonalMoneyEvents
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog
from app.domains.reference_data.expense_taxonomy import validate_expense_category_pair


def resolve_spend_category_code(spend_category: object) -> str | None:
    """Map lifestyle spend labels (or codes) to EXPENSE taxonomy parents."""
    if spend_category is None:
        return None
    raw = str(spend_category).strip()
    if not raw:
        return None
    if raw in SPEND_CATEGORY_TO_EXPENSE_CODE:
        return SPEND_CATEGORY_TO_EXPENSE_CODE[raw]
    upper = raw.upper().replace(" ", "_").replace("&", "AND")
    # Already a taxonomy code
    for code in SPEND_CATEGORY_TO_EXPENSE_CODE.values():
        if code == raw.upper() or code == upper:
            return code
    # Case-insensitive label match
    for label, code in SPEND_CATEGORY_TO_EXPENSE_CODE.items():
        if label.lower() == raw.lower():
            return code
    return None


def amount_minor_from_data(
    data: dict[str, Any],
    *,
    catalog: ReferenceCatalog | None = None,
    currency_code: str | None = None,
) -> int:
    ref = catalog or get_reference_catalog()
    code = (currency_code or data.get("currency_code") or "").strip().upper() or _default_currency(ref)
    if data.get("amount_minor") is not None:
        try:
            return max(0, int(data["amount_minor"]))
        except (TypeError, ValueError):
            pass
    amount_raw = data.get("amount")
    if amount_raw is not None and str(amount_raw).strip() != "":
        return ref.minor_from_major_string(str(amount_raw), code)
    return 0


def _default_currency(catalog: ReferenceCatalog) -> str:
    try:
        from app.domains.group.expense_contract import resolve_group_default_currency

        return resolve_group_default_currency({})
    except Exception:
        return "INR"


async def insert_money_event(
    ctx: QuickAddContext,
    *,
    source_event_type: str,
    money_event_type: str,
    data: dict[str, Any],
    currency_code: str | None = None,
    category_code: str | None = None,
    account_id: UUID | None = None,
    impact_label: str | None = None,
) -> tuple[PersonalMoneyEvents, float]:
    catalog = get_reference_catalog()
    currency = str(
        data.get("currency_code") or currency_code or _default_currency(catalog)
    ).upper()
    amount_minor = amount_minor_from_data(data, catalog=catalog, currency_code=currency)
    amount = catalog.major_from_minor(amount_minor, currency)
    resolved_category = category_code or str(data.get("category_code") or "OTHER")
    if not category_code and data.get("category_name"):
        resolved = catalog.resolve_category_code(
            "expense_categories",
            None,
            data.get("category_name"),
        )
        if resolved:
            resolved_category = resolved
    if data.get("spend_category"):
        mapped = resolve_spend_category_code(data.get("spend_category"))
        resolved_category = mapped or str(data["spend_category"])[:80]

    raw_sub = data.get("subcategory_code")
    if "subcategory_code" in data and data.get("subcategory_code") is None:
        raw_sub = None
    elif raw_sub is None:
        raw_sub = data.get("subcategory") or data.get("sub_category") or data.get("expense_subcategory")

    cat, sub = validate_expense_category_pair(
        resolved_category,
        None if raw_sub in ("", None) else str(raw_sub),
        catalog=catalog,
    )
    resolved_category = cat or resolved_category

    row = PersonalMoneyEvents(
        quick_add_event_id=ctx.quick_add_event_id,
        moment_id=ctx.moment_id,
        user_id=ctx.user_id,
        moment_type_code=ctx.moment_type_code,
        source_event_type=source_event_type,
        linked_event_id=ctx.quick_add_event_id,
        money_event_type=money_event_type,
        title=str(ctx.event_title or "").strip()[:150] or "Money entry",
        amount=amount,
        amount_minor=amount_minor,
        currency_code=currency,
        category_code=(resolved_category or "OTHER")[:80],
        subcategory_code=(sub[:80] if sub else None),
        account_id=account_id,
        direction=money_direction(money_event_type),
        impact_label=(impact_label or str(data.get("pressure_impact") or ""))[:80] or None,
        financial_pressure_score=pressure_score(str(data.get("pressure_impact") or "")),
    )
    ctx.session.add(row)
    await ctx.session.flush()
    return row, float(amount)


def money_timeline_draft(
    ctx: QuickAddContext,
    *,
    amount: float,
    subtitle: str | None = None,
    impact: dict[str, Any] | None = None,
) -> TimelineDraft:
    return TimelineDraft(
        display_title=ctx.event_title,
        display_subtitle=subtitle,
        display_amount=amount if amount > 0 else None,
        impact_labels=impact,
    )


def optional_account_id(data: dict[str, Any]) -> UUID | None:
    raw = data.get("account_id")
    if not raw:
        return None
    try:
        return UUID(str(raw))
    except ValueError:
        return None
