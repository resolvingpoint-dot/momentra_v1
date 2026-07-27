"""EXPENSE → personal_money_events."""
from __future__ import annotations

from uuid import UUID

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import (
    money_direction,
    pressure_score,
)
from app.domains.personal.models import PersonalMoneyEvents
from app.domains.reference_data.catalog import get_reference_catalog


def resolve_money_event_title(
    expense: dict,
    *,
    event_title: str | None,
    category_label: str | None = None,
) -> str:
    """Prefer expense.title, then event_title, then category label, then fallback."""
    for candidate in (
        expense.get("title"),
        expense.get("description"),
        event_title,
        category_label,
        "Money entry",
    ):
        text = str(candidate or "").strip()
        if text:
            return text[:150]
    return "Money entry"


class ExpenseHandler:
    event_type = "EXPENSE"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        expense = ctx.body.get("expense") or {}
        catalog = get_reference_catalog()

        transaction_type = str(expense.get("transaction_type") or "EXPENSE").upper()
        amount_minor = int(expense.get("amount_minor") or 0)
        currency_code = str(expense.get("currency_code") or "INR").upper()
        category_code = str(expense.get("category_code") or "OTHER")
        subcategory_code = expense.get("subcategory_code")
        account_id_raw = expense.get("account_id")
        account_id = UUID(str(account_id_raw)) if account_id_raw else None
        amount = catalog.major_from_minor(amount_minor, currency_code)
        category_label = catalog.label_for("expense_categories", category_code)
        title = resolve_money_event_title(
            expense if isinstance(expense, dict) else {},
            event_title=ctx.event_title,
            category_label=category_label,
        )

        row = PersonalMoneyEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            moment_type_code=ctx.moment_type_code,
            source_event_type="EXPENSE",
            linked_event_id=ctx.quick_add_event_id,
            money_event_type=transaction_type,
            title=title,
            amount=amount,
            amount_minor=amount_minor,
            currency_code=currency_code,
            category_code=category_code,
            subcategory_code=str(subcategory_code)[:80] if subcategory_code else None,
            account_id=account_id,
            direction=money_direction(transaction_type),
            impact_label=str(expense.get("pressure_impact") or "")[:80] or None,
            financial_pressure_score=pressure_score(
                str(expense.get("pressure_impact") or "")
            ),
        )
        ctx.session.add(row)
        await ctx.session.flush()

        subtitle = category_label
        if expense.get("pressure_impact"):
            subtitle = f"{category_label} · {expense['pressure_impact']}"
        return TimelineDraft(
            display_title=title,
            display_subtitle=subtitle,
            display_amount=float(amount),
            impact_labels={"pressure_impact": expense.get("pressure_impact")},
        )
