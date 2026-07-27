"""Upsert Business Runway specialty tables for the same shared moment UUID."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import (
    BusinessRunwayGovernanceRules,
    BusinessRunwaySetup,
    BusinessRunwayStructure,
)
from app.domains.business.setup.runway_mappers import (
    compute_derived_preview,
    funding_sources_to_sql_primary,
    minor_to_major,
    revenue_model_to_sql,
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def upsert_runway_setup(
    session: AsyncSession,
    *,
    moment_id: UUID,
    owner_user_id: UUID,
    answers: dict[str, Any],
) -> None:
    currency = (answers.get("operating_currency_code") or "INR").upper()
    cash_minor = int(answers.get("current_cash_minor") or 0)
    burn_minor = int(answers.get("monthly_burn_minor") or 0)
    rev_minor = answers.get("estimated_monthly_revenue_minor")
    rev_minor_i = int(rev_minor) if rev_minor is not None else 0
    derived = compute_derived_preview(answers)
    estimated = derived.get("estimated_runway_months")
    stage = answers.get("business_stage") or "CUSTOM"
    extras = {
        "runway_name": answers.get("runway_name"),
        "moment_name": answers.get("moment_name"),
        "allow_multi_currency": answers.get("allow_multi_currency"),
        "financial_year_start": answers.get("financial_year_start"),
        "default_currency_code": answers.get("default_currency_code"),
        "expected_team_growth_impact": answers.get("expected_team_growth_impact"),
    }
    now = _now()
    payload = {
        "business_stage": stage,
        "cash_available": minor_to_major(cash_minor, currency),
        "monthly_burn": minor_to_major(burn_minor, currency),
        "monthly_revenue": minor_to_major(rev_minor_i, currency),
        "operating_currency": currency,
        "estimated_runway_months": Decimal(str(estimated or 0)),
        "runway_goal": None,
        "runway_owner_id": owner_user_id,
        "current_cash_minor": cash_minor,
        "monthly_burn_minor": burn_minor,
        "estimated_monthly_revenue_minor": int(rev_minor) if rev_minor is not None else None,
        "runway_goal_months": answers.get("runway_goal_months"),
        "revenue_status": answers.get("revenue_status"),
        "country_code": answers.get("country_code"),
        "locale": answers.get("locale"),
        "timezone": answers.get("timezone"),
        "setup_extras": extras,
        "updated_at": now,
    }
    result = await session.execute(
        select(BusinessRunwaySetup).where(BusinessRunwaySetup.moment_id == moment_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(BusinessRunwaySetup(moment_id=moment_id, created_at=now, **payload))
    else:
        for k, v in payload.items():
            setattr(row, k, v)
    await session.flush()


async def upsert_runway_structure(
    session: AsyncSession,
    *,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    burn = answers.get("burn_categories") or []
    if isinstance(burn, list):
        burn_json: dict | list = {"categories": burn}
    elif isinstance(burn, dict):
        burn_json = burn
    else:
        burn_json = {"categories": []}

    sources = answers.get("funding_sources") or []
    alert = answers.get("runway_alert_threshold_months") or 6
    model = answers.get("revenue_model")
    now = _now()
    extras = {
        "expected_team_growth_impact": answers.get("expected_team_growth_impact"),
        "allow_multi_currency": answers.get("allow_multi_currency"),
        "financial_year_start": answers.get("financial_year_start"),
    }
    payload = {
        "burn_categories": burn_json,
        "revenue_model": revenue_model_to_sql(model),
        "alert_threshold_months": Decimal(str(alert)),
        "funding_structure": funding_sources_to_sql_primary(sources if isinstance(sources, list) else None),
        "runway_philosophy": "balanced",
        "monitoring_level": "standard",
        "runway_alert_threshold_months": int(alert),
        "collection_rate_percent": answers.get("collection_rate_percent"),
        "funding_sources": {"sources": sources} if isinstance(sources, list) else sources,
        "revenue_model_canonical": model,
        "structure_extras": extras,
        "updated_at": now,
    }
    result = await session.execute(
        select(BusinessRunwayStructure).where(BusinessRunwayStructure.moment_id == moment_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(BusinessRunwayStructure(moment_id=moment_id, created_at=now, **payload))
    else:
        for k, v in payload.items():
            setattr(row, k, v)
    await session.flush()


async def upsert_runway_governance(
    session: AsyncSession,
    *,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    approval_required = bool(
        answers.get("approval_required_for_funding_changes")
        or answers.get("approval_required_for_cash_adjustments")
        or answers.get("approval_required_for_large_expenses")
        or answers.get("approval_required_for_threshold_changes")
    )
    vis = answers.get("visibility") or "TEAM"
    prefs = answers.get("notification_preferences") if isinstance(answers.get("notification_preferences"), dict) else {}
    now = _now()
    extras = {
        "approval_required_for_funding_changes": answers.get("approval_required_for_funding_changes"),
        "approval_required_for_cash_adjustments": answers.get("approval_required_for_cash_adjustments"),
        "approval_required_for_large_expenses": answers.get("approval_required_for_large_expenses"),
        "approval_required_for_threshold_changes": answers.get("approval_required_for_threshold_changes"),
        "approval_owner_id": answers.get("approval_owner_id"),
        "invite_on_activation": answers.get("invite_on_activation"),
        "notify_members": answers.get("notify_members"),
        "notification_preferences": prefs,
    }
    payload = {
        "visibility_roles": {"visibility": vis},
        "alert_recipient_roles": {"roles": ["OWNER", "FINANCE_LEAD"]},
        "alert_conditions": {
            "runway_alert_threshold_months": answers.get("runway_alert_threshold_months"),
        },
        "approval_required": approval_required,
        "approval_rules": {
            "large_expense_threshold_minor": answers.get("large_expense_threshold_minor"),
            "approval_owner_id": answers.get("approval_owner_id"),
        },
        "large_expense_threshold_minor": answers.get("large_expense_threshold_minor"),
        "visibility": vis,
        "governance_extras": extras,
        "updated_at": now,
    }
    result = await session.execute(
        select(BusinessRunwayGovernanceRules).where(
            BusinessRunwayGovernanceRules.moment_id == moment_id
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(BusinessRunwayGovernanceRules(moment_id=moment_id, created_at=now, **payload))
    else:
        for k, v in payload.items():
            setattr(row, k, v)
    await session.flush()
