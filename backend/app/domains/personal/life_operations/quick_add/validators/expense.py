"""Validate Life Ops EXPENSE quick-add payloads."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.models import PersonalAccounts
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog


async def validate_account_ownership(
    session: AsyncSession,
    user_id: UUID,
    account_id_raw: Any,
) -> UUID:
    if account_id_raw is None or str(account_id_raw).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.account_id is required",
        )
    try:
        account_id = UUID(str(account_id_raw))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.account_id must be a valid UUID",
        ) from exc

    result = await session.execute(
        select(PersonalAccounts).where(
            PersonalAccounts.account_id == account_id,
            PersonalAccounts.user_id == user_id,
            PersonalAccounts.is_active.is_(True),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.account_id not found or inactive",
        )
    return account_id


async def validate_expense_payload(
    body: dict[str, Any],
    *,
    session: AsyncSession,
    user_id: UUID,
    catalog: ReferenceCatalog | None = None,
) -> dict[str, Any]:
    ref = catalog or get_reference_catalog()
    expense = body.get("expense") or {}

    currency_code = expense.get("currency_code")
    amount_minor = expense.get("amount_minor")

    if currency_code is None or str(currency_code).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.currency_code is required",
        )
    currency_code = ref.validate_currency(str(currency_code))

    if amount_minor is None:
        legacy_amount = expense.get("amount")
        if legacy_amount is not None and str(legacy_amount).strip() != "":
            amount_minor = ref.minor_from_major_string(str(legacy_amount), currency_code)
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="expense.amount_minor is required",
            )

    try:
        amount_minor_int = int(amount_minor)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.amount_minor must be an integer",
        ) from exc

    if amount_minor_int < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.amount_minor must be >= 0",
        )

    category_code = ref.resolve_category_code(
        "expense_categories",
        expense.get("category_code"),
        expense.get("category_name"),
    )
    if not category_code:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expense.category_code is required",
        )

    from app.domains.reference_data.expense_taxonomy import (
        InvalidExpenseSubcategoryError,
        validate_expense_category_pair,
    )

    if "subcategory_code" in expense:
        raw_sub = expense.get("subcategory_code")
    else:
        raw_sub = (
            expense.get("subcategory")
            or expense.get("sub_category")
            or expense.get("expense_subcategory")
        )
    try:
        category_code, subcategory_code = validate_expense_category_pair(
            category_code,
            raw_sub,
        )
    except InvalidExpenseSubcategoryError:
        raise

    account_id = await validate_account_ownership(
        session, user_id, expense.get("account_id")
    )

    return {
        "currency_code": currency_code,
        "amount_minor": amount_minor_int,
        "category_code": category_code,
        "subcategory_code": subcategory_code,
        "account_id": str(account_id),
        "transaction_type": str(expense.get("transaction_type") or "EXPENSE").upper(),
        "pressure_impact": expense.get("pressure_impact"),
    }
