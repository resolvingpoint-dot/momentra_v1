"""Handler: CASH_INFLOW → runway_cash_inflows."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import minor_to_decimal, parse_date
from app.domains.business.models import BusinessActivityEvents, BusinessMoments, RunwayCashInflows

_INFLOW_TYPES = {
    "revenue_collected",
    "investor_funding",
    "owner_contribution",
    "bank_loan",
    "government_grant",
    "customer_advance",
    "refund",
    "other",
}


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    if event.business_moment_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cash inflow requires an activated business moment",
        )
    exists = await session.execute(
        select(BusinessMoments.moment_id).where(
            BusinessMoments.moment_id == event.business_moment_id
        )
    )
    if exists.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business moment root row is missing — re-activate setup and try again",
        )

    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    amount_minor = payload.get("amount_minor")
    if amount_minor is not None:
        amount = minor_to_decimal(amount_minor, currency=currency)
    else:
        amount = Decimal(str(payload.get("amount", 0)))
        amount_minor = (
            int(amount * 100)
            if currency.upper() not in {"JPY", "KRW", "VND", "KWD", "BHD", "OMR"}
            else int(amount)
        )
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cash inflow amount must be greater than zero",
        )
    fx_raw = payload.get("exchange_rate_to_operating_currency", 1)
    try:
        fx = Decimal(str(fx_raw))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exchange rate",
        ) from exc
    if fx <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exchange rate must be greater than zero",
        )

    inflow_type = str(payload.get("inflow_type") or "revenue_collected").lower()
    if inflow_type not in _INFLOW_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported inflow_type: {inflow_type}",
        )

    row = RunwayCashInflows(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        inflow_type=inflow_type,
        amount=amount,
        currency=currency,
        currency_code=currency,
        amount_minor=int(amount_minor or 0),
        exchange_rate_to_operating_currency=fx,
        amount_in_operating_currency=amount * fx,
        inflow_date=parse_date(payload.get("inflow_date")),
        created_by=event.created_by,
        reference=payload.get("reference"),
        description=payload.get("description"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.cash_inflow_id
