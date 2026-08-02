"""Runway template builder — builds RunwayContext from SQL."""
from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.domains.business.models import (
    BusinessActivityEvents,
    BusinessMomentMembers,
    BusinessMoments,
    BusinessMomentSetup,
    BusinessRunwaySetup,
    BusinessRunwayStructure,
    RunwayCashInflows,
    RunwayExpenseBurns,
    RunwayFinancialUpdates,
    RunwayRisks,
    RunwayStrategicDecisions,
)
from app.domains.business.templates.business_runway.context import RunwayContext
from app.domains.business.templates.business_runway.projector import refresh_runway_projections
from app.domains.business.templates.business_runway.series_helpers import (
    net_burn_minor,
    runway_months,
)


def _minor_from_row(row, minor_attr: str, decimal_attr: str) -> int:
    if row is None:
        return 0
    minor_val = getattr(row, minor_attr, None)
    if minor_val is not None:
        return int(minor_val)
    dec = getattr(row, decimal_attr, None)
    if dec is not None:
        return int(float(dec) * 100)
    return 0


async def _with_session(coro_factory):
    if async_session_factory is None:
        raise RuntimeError("DATABASE_URL not configured")
    async with async_session_factory() as session:
        return await coro_factory(session)


async def _count_members(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(BusinessMomentMembers)
        .where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.member_status.in_(["active", "configured"]),
        )
    )
    return int(result.scalar() or 0)


async def _sum_inflow(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.coalesce(func.sum(RunwayCashInflows.amount_in_operating_currency), 0)).where(
            RunwayCashInflows.moment_id == moment_id
        )
    )
    return int((result.scalar() or 0) * 100)


async def _sum_burn(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.coalesce(func.sum(RunwayExpenseBurns.amount_in_operating_currency), 0)).where(
            RunwayExpenseBurns.moment_id == moment_id
        )
    )
    return int((result.scalar() or 0) * 100)


async def _count_risks(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(RunwayRisks)
        .where(
            RunwayRisks.moment_id == moment_id,
            RunwayRisks.risk_status == "open",
        )
    )
    return int(result.scalar() or 0)


async def _count_decisions(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(RunwayStrategicDecisions)
        .where(
            RunwayStrategicDecisions.moment_id == moment_id,
            RunwayStrategicDecisions.decision_status == "active",
        )
    )
    return int(result.scalar() or 0)


async def _count_financial_updates(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(RunwayFinancialUpdates)
        .where(RunwayFinancialUpdates.moment_id == moment_id)
    )
    return int(result.scalar() or 0)


async def _load_activity(session: AsyncSession, moment_id: UUID) -> list[dict[str, Any]]:
    events = await session.execute(
        select(BusinessActivityEvents)
        .where(
            BusinessActivityEvents.business_moment_id == moment_id,
            BusinessActivityEvents.is_voided.is_(False),
        )
        .order_by(BusinessActivityEvents.occurred_at.desc())
        .limit(50)
    )
    activity_rows = list(events.scalars().all())
    return [
        {
            "event_id": str(e.event_id),
            "action_type": e.action_type,
            "title": e.title,
            "subtitle": e.subtitle,
            "occurred_at": str(e.occurred_at),
            "is_voided": e.is_voided,
            "source_moment_id": str(moment_id),
        }
        for e in activity_rows
    ]


async def _load_runway_sections_concurrent(moment_id: UUID) -> tuple:
    return await asyncio.gather(
        _with_session(lambda s: _count_members(s, moment_id)),
        _with_session(lambda s: _sum_inflow(s, moment_id)),
        _with_session(lambda s: _sum_burn(s, moment_id)),
        _with_session(lambda s: _count_risks(s, moment_id)),
        _with_session(lambda s: _count_decisions(s, moment_id)),
        _with_session(lambda s: _count_financial_updates(s, moment_id)),
        _with_session(lambda s: _load_activity(s, moment_id)),
    )


class RunwayTemplateBuilder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build(self, user_id: UUID, moment_id: UUID) -> RunwayContext:
        biz = await self.session.execute(
            select(BusinessMoments).where(BusinessMoments.moment_id == moment_id)
        )
        moment = biz.scalar_one_or_none()
        if moment is None:
            raise ValueError(f"BusinessMoment {moment_id} not found")

        setup_row = await self.session.execute(
            select(BusinessMomentSetup).where(BusinessMomentSetup.moment_id == moment_id)
        )
        setup = setup_row.scalar_one_or_none()

        runway_setup_row = await self.session.execute(
            select(BusinessRunwaySetup).where(BusinessRunwaySetup.moment_id == moment_id)
        )
        runway_setup = runway_setup_row.scalar_one_or_none()

        structure_row = await self.session.execute(
            select(BusinessRunwayStructure).where(BusinessRunwayStructure.moment_id == moment_id)
        )
        structure = structure_row.scalar_one_or_none()

        currency = (
            (runway_setup.operating_currency if runway_setup else None)
            or (setup.currency if setup else None)
            or "INR"
        )

        (
            member_count,
            total_inflow,
            total_burn,
            risk_count,
            decision_count,
            financial_update_count,
            activities,
        ) = await _load_runway_sections_concurrent(moment_id)

        cash_avail = _minor_from_row(runway_setup, "current_cash_minor", "cash_available")
        monthly_burn_setup = _minor_from_row(runway_setup, "monthly_burn_minor", "monthly_burn")
        monthly_revenue = _minor_from_row(
            runway_setup, "estimated_monthly_revenue_minor", "monthly_revenue"
        )

        nb_activity = net_burn_minor(total_inflow, total_burn)
        effective_burn = (
            max(monthly_burn_setup, nb_activity)
            if monthly_burn_setup > 0
            else (nb_activity if nb_activity > 0 else monthly_burn_setup)
        )
        rm = runway_months(cash_avail, effective_burn) if effective_burn > 0 else None

        collection_rate = structure.collection_rate_percent if structure else None
        alert_threshold = None
        if structure is not None:
            if structure.runway_alert_threshold_months is not None:
                alert_threshold = float(structure.runway_alert_threshold_months)
            else:
                alert_threshold = float(structure.alert_threshold_months)

        ctx = RunwayContext(
            moment=moment,
            moment_id=moment.moment_id,
            moment_type="BUSINESS_RUNWAY",
            moment_name=moment.moment_name or "Runway",
            status=(moment.status or "draft"),
            is_active=(moment.status or "").lower() == "active",
            member_count=member_count,
            activity_count=len(activities),
            activities=activities,
            operating_currency=currency,
            runway_name=moment.moment_name or "Runway",
            total_inflow_minor=total_inflow,
            total_burn_minor=total_burn,
            net_burn_minor=nb_activity,
            monthly_burn_setup_minor=monthly_burn_setup,
            monthly_revenue_minor=monthly_revenue,
            collection_rate_percent=collection_rate,
            runway_goal_months=(runway_setup.runway_goal_months if runway_setup else None),
            alert_threshold_months=alert_threshold,
            revenue_status=(runway_setup.revenue_status if runway_setup else None),
            runway_months=rm,
            cash_available_minor=cash_avail,
            risk_count=risk_count,
            decision_count=decision_count,
            financial_update_count=financial_update_count,
        )
        ctx.projection = refresh_runway_projections(ctx)
        return ctx
