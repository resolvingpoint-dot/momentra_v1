"""Operations template builder — one-pass OpsContext from SQL."""
from __future__ import annotations

import asyncio
import time
from datetime import date, datetime, timedelta, timezone
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
    BusinessOperationsBudgetCategories,
    BusinessOperationsGovernanceRules,
    BusinessOperationsSetup,
    OperationsApprovalRequests,
    OperationsImprovements,
    OperationsIssues,
    OperationsSpendEntries,
    OperationsVendorUpdates,
)
from app.domains.business.templates.business_operations.context import OpsContext
from app.domains.business.templates.business_operations.projector import refresh_ops_projections
from app.domains.business.templates.business_operations.series_helpers import budget_usage_pct
from app.domains.business.vendor_suggestions import list_moment_vendors, vendor_due_lookup


def _minor_from_decimal(value, *, currency: str = "INR") -> int:
    if value is None:
        return 0
    # Prefer minor units already stored when available; else assume 2-decimal major.
    if currency.upper() in {"JPY", "KRW", "VND"}:
        return int(value)
    if currency.upper() in {"KWD", "BHD", "OMR"}:
        return int(float(value) * 1000)
    return int(float(value) * 100)


def _stage(timings: dict[str, float], name: str, start: float) -> None:
    timings[name] = round((time.perf_counter() - start) * 1000, 2)


async def _with_session(coro_factory):
    if async_session_factory is None:
        raise RuntimeError("DATABASE_URL not configured")
    async with async_session_factory() as session:
        return await coro_factory(session)


async def _load_members(session: AsyncSession, moment_id: UUID) -> dict[str, Any]:
    members = await session.execute(
        select(BusinessMomentMembers).where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.member_status.in_(["active", "configured"]),
        )
    )
    member_rows = list(members.scalars().all())
    picker = [
        {
            "member_id": str(m.member_id),
            "name": m.name,
            "role": m.role,
            "user_id": str(m.user_id) if m.user_id else None,
        }
        for m in member_rows
    ]
    owner = next(
        (
            m
            for m in member_rows
            if "owner" in (m.role or "").lower() or (m.role or "").upper() == "OWNER"
        ),
        None,
    )
    owner_name = (owner.name if owner else None) or (
        str(owner.user_id) if owner and owner.user_id else None
    )
    return {
        "rows": member_rows,
        "count": len(member_rows),
        "picker": picker,
        "owner_name": owner_name,
    }


async def _load_vendor_kpis(
    session: AsyncSession, moment_id: UUID
) -> tuple[int, int, dict[str, int]]:
    total = await session.execute(
        select(func.count())
        .select_from(OperationsVendorUpdates)
        .where(
            OperationsVendorUpdates.moment_id == moment_id,
            OperationsVendorUpdates.is_voided.is_(False),
        )
    )
    critical = await session.execute(
        select(func.count())
        .select_from(OperationsVendorUpdates)
        .where(
            OperationsVendorUpdates.moment_id == moment_id,
            OperationsVendorUpdates.is_voided.is_(False),
            func.lower(OperationsVendorUpdates.impact_level).in_(["critical", "high"]),
        )
    )
    vendors = await list_moment_vendors(session, moment_id)
    return (
        int(total.scalar_one() or 0),
        int(critical.scalar_one() or 0),
        vendor_due_lookup(vendors),
    )


async def _load_approval_kpis(
    session: AsyncSession, moment_id: UUID, today: date, recent_cut: datetime
) -> dict[str, Any]:
    pending = await session.execute(
        select(func.count())
        .select_from(OperationsApprovalRequests)
        .where(
            OperationsApprovalRequests.moment_id == moment_id,
            OperationsApprovalRequests.is_voided.is_(False),
            OperationsApprovalRequests.approval_status == "pending",
        )
    )
    overdue = await session.execute(
        select(func.count())
        .select_from(OperationsApprovalRequests)
        .where(
            OperationsApprovalRequests.moment_id == moment_id,
            OperationsApprovalRequests.is_voided.is_(False),
            OperationsApprovalRequests.approval_status == "pending",
            OperationsApprovalRequests.due_date.is_not(None),
            OperationsApprovalRequests.due_date < today,
        )
    )
    amount = await session.execute(
        select(func.coalesce(func.sum(OperationsApprovalRequests.amount_minor), 0)).where(
            OperationsApprovalRequests.moment_id == moment_id,
            OperationsApprovalRequests.is_voided.is_(False),
            OperationsApprovalRequests.approval_status == "pending",
        )
    )
    # Recent approved/rejected still need updated_at filter — light row fetch capped
    recent_rows = await session.execute(
        select(
            OperationsApprovalRequests.approval_status,
            OperationsApprovalRequests.updated_at,
        ).where(
            OperationsApprovalRequests.moment_id == moment_id,
            OperationsApprovalRequests.is_voided.is_(False),
            OperationsApprovalRequests.approval_status.in_(["approved", "rejected"]),
            OperationsApprovalRequests.updated_at >= recent_cut.replace(tzinfo=None),
        )
    )
    approved_recently = 0
    rejected_recently = 0
    for status_val, updated_at in recent_rows.all():
        if not updated_at:
            continue
        ts = (
            updated_at.replace(tzinfo=timezone.utc)
            if updated_at.tzinfo is None
            else updated_at
        )
        if ts < recent_cut:
            continue
        if status_val == "approved":
            approved_recently += 1
        elif status_val == "rejected":
            rejected_recently += 1
    amt = int(amount.scalar_one() or 0)
    return {
        "pending": int(pending.scalar_one() or 0),
        "overdue": int(overdue.scalar_one() or 0),
        "approved_recently": approved_recently,
        "rejected_recently": rejected_recently,
        "amount_awaiting": amt if amt else None,
    }


async def _load_issue_kpis(
    session: AsyncSession, moment_id: UUID, today: date, recent_cut: datetime
) -> dict[str, Any]:
    open_statuses = ("open", "investigating")
    open_c = await session.execute(
        select(func.count())
        .select_from(OperationsIssues)
        .where(
            OperationsIssues.moment_id == moment_id,
            OperationsIssues.is_voided.is_(False),
            OperationsIssues.issue_status.in_(open_statuses),
        )
    )
    critical = await session.execute(
        select(func.count())
        .select_from(OperationsIssues)
        .where(
            OperationsIssues.moment_id == moment_id,
            OperationsIssues.is_voided.is_(False),
            OperationsIssues.issue_status.in_(open_statuses),
            func.lower(OperationsIssues.severity) == "critical",
        )
    )
    overdue = await session.execute(
        select(func.count())
        .select_from(OperationsIssues)
        .where(
            OperationsIssues.moment_id == moment_id,
            OperationsIssues.is_voided.is_(False),
            OperationsIssues.issue_status.in_(open_statuses),
            OperationsIssues.target_resolution_date.is_not(None),
            OperationsIssues.target_resolution_date < today,
        )
    )
    unassigned = await session.execute(
        select(func.count())
        .select_from(OperationsIssues)
        .where(
            OperationsIssues.moment_id == moment_id,
            OperationsIssues.is_voided.is_(False),
            OperationsIssues.issue_status.in_(open_statuses),
            OperationsIssues.owner_id.is_(None),
        )
    )
    resolved = await session.execute(
        select(func.count())
        .select_from(OperationsIssues)
        .where(
            OperationsIssues.moment_id == moment_id,
            OperationsIssues.is_voided.is_(False),
            OperationsIssues.issue_status == "resolved",
            OperationsIssues.resolved_at.is_not(None),
            OperationsIssues.resolved_at >= recent_cut.replace(tzinfo=None),
        )
    )
    return {
        "open": int(open_c.scalar_one() or 0),
        "critical": int(critical.scalar_one() or 0),
        "overdue": int(overdue.scalar_one() or 0),
        "unassigned": int(unassigned.scalar_one() or 0),
        "resolved_recently": int(resolved.scalar_one() or 0),
    }


async def _load_improvement_kpis(session: AsyncSession, moment_id: UUID) -> dict[str, int]:
    planned = await session.execute(
        select(func.count())
        .select_from(OperationsImprovements)
        .where(
            OperationsImprovements.moment_id == moment_id,
            OperationsImprovements.is_voided.is_(False),
            OperationsImprovements.improvement_status.in_(["recorded", "planned"]),
        )
    )
    in_progress = await session.execute(
        select(func.count())
        .select_from(OperationsImprovements)
        .where(
            OperationsImprovements.moment_id == moment_id,
            OperationsImprovements.is_voided.is_(False),
            OperationsImprovements.improvement_status.in_(["in_follow_up", "in_progress"]),
        )
    )
    completed = await session.execute(
        select(func.count())
        .select_from(OperationsImprovements)
        .where(
            OperationsImprovements.moment_id == moment_id,
            OperationsImprovements.is_voided.is_(False),
            OperationsImprovements.improvement_status.in_(["completed", "done"]),
        )
    )
    return {
        "planned": int(planned.scalar_one() or 0),
        "in_progress": int(in_progress.scalar_one() or 0),
        "completed": int(completed.scalar_one() or 0),
    }


async def _load_activity(session: AsyncSession, moment_id: UUID) -> dict[str, Any]:
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
    activities = [
        {
            "event_id": str(e.event_id),
            "action_type": e.action_type,
            "title": e.title,
            "subtitle": e.subtitle,
            "occurred_at": str(e.occurred_at),
            "is_voided": e.is_voided,
            "source_moment_id": str(moment_id),
            "payload": e.payload or {},
            "created_by": str(e.created_by) if e.created_by else None,
        }
        for e in activity_rows
    ]
    return {
        "activities": activities,
        "last_updated": str(activity_rows[0].occurred_at) if activity_rows else None,
    }


async def _load_ops_sections_concurrent(
    moment_id: UUID, today: date, recent_cut: datetime
) -> tuple:
    return await asyncio.gather(
        _with_session(lambda s: _load_members(s, moment_id)),
        _with_session(lambda s: _load_vendor_kpis(s, moment_id)),
        _with_session(lambda s: _load_approval_kpis(s, moment_id, today, recent_cut)),
        _with_session(lambda s: _load_issue_kpis(s, moment_id, today, recent_cut)),
        _with_session(lambda s: _load_improvement_kpis(s, moment_id)),
        _with_session(lambda s: _load_activity(s, moment_id)),
    )


class OpsTemplateBuilder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build(self, user_id: UUID, moment_id: UUID) -> OpsContext:
        timings: dict[str, float] = {}
        t0 = time.perf_counter()

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

        ops_setup_row = await self.session.execute(
            select(BusinessOperationsSetup).where(BusinessOperationsSetup.moment_id == moment_id)
        )
        ops_setup = ops_setup_row.scalar_one_or_none()

        gov_row = await self.session.execute(
            select(BusinessOperationsGovernanceRules).where(
                BusinessOperationsGovernanceRules.moment_id == moment_id
            )
        )
        governance = gov_row.scalar_one_or_none()

        currency = (
            (ops_setup.operating_currency if ops_setup else None)
            or (setup.currency if setup else None)
            or "INR"
        )
        monthly_budget_minor = 0
        if ops_setup:
            if ops_setup.monthly_budget_minor is not None:
                monthly_budget_minor = int(ops_setup.monthly_budget_minor)
            else:
                monthly_budget_minor = _minor_from_decimal(
                    ops_setup.monthly_operating_budget, currency=currency
                )
        _stage(timings, "profile", t0)

        t = time.perf_counter()
        categories = await self.session.execute(
            select(BusinessOperationsBudgetCategories).where(
                BusinessOperationsBudgetCategories.moment_id == moment_id,
                BusinessOperationsBudgetCategories.category_status == "active",
            )
        )
        category_rows = list(categories.scalars().all())
        total_budget_from_cats = sum(
            _minor_from_decimal(c.allocated_budget, currency=c.currency or currency)
            for c in category_rows
        )
        total_budget_minor = monthly_budget_minor or total_budget_from_cats

        spend_by_cat = await self.session.execute(
            select(
                OperationsSpendEntries.budget_category_id,
                func.coalesce(func.sum(OperationsSpendEntries.amount_in_operating_currency), 0),
            )
            .where(
                OperationsSpendEntries.moment_id == moment_id,
                OperationsSpendEntries.is_voided.is_(False),
            )
            .group_by(OperationsSpendEntries.budget_category_id)
        )
        spend_map = {row[0]: _minor_from_decimal(row[1], currency=currency) for row in spend_by_cat.all()}

        spend_sum = await self.session.execute(
            select(func.coalesce(func.sum(OperationsSpendEntries.amount_in_operating_currency), 0)).where(
                OperationsSpendEntries.moment_id == moment_id,
                OperationsSpendEntries.is_voided.is_(False),
            )
        )
        total_spend = _minor_from_decimal(spend_sum.scalar() or 0, currency=currency)

        allocations: list[dict] = []
        over_budget: list[dict] = []
        allocated_sum = 0
        for cat in category_rows:
            allocated = _minor_from_decimal(cat.allocated_budget, currency=cat.currency or currency)
            spent = int(spend_map.get(cat.budget_category_id, 0))
            allocated_sum += allocated
            item = {
                "budget_category_id": str(cat.budget_category_id),
                "label": cat.category_name,
                "allocated_minor": allocated,
                "spent_minor": spent,
                "remaining_minor": allocated - spent,
            }
            allocations.append(item)
            if spent > allocated and allocated > 0:
                over_budget.append(item)
        unallocated = max(0, total_budget_minor - allocated_sum) if total_budget_minor else 0
        remaining = total_budget_minor - total_spend
        usage = budget_usage_pct(total_spend, total_budget_minor)
        _stage(timings, "budget", t)

        t = time.perf_counter()
        # spend already loaded above
        _stage(timings, "spend", t)

        today = date.today()
        recent_cut = datetime.now(timezone.utc) - timedelta(days=14)

        # Independent KPI/list loads — separate sessions so gather is safe.
        t = time.perf_counter()
        (
            member_bundle,
            vendor_kpis,
            approval_kpis,
            issue_kpis,
            improvement_kpis,
            activity_bundle,
        ) = await _load_ops_sections_concurrent(moment_id, today, recent_cut)
        member_rows = member_bundle["rows"]
        member_count = member_bundle["count"]
        member_picker = member_bundle["picker"]
        owner_name = member_bundle["owner_name"]
        vendor_count, critical_vendor_count, vendor_due_by_name = vendor_kpis
        pending_approvals = approval_kpis["pending"]
        overdue_approval_count = approval_kpis["overdue"]
        approved_recently = approval_kpis["approved_recently"]
        rejected_recently = approval_kpis["rejected_recently"]
        amount_awaiting = approval_kpis["amount_awaiting"]
        open_issue_count = issue_kpis["open"]
        critical_issue_count = issue_kpis["critical"]
        overdue_issue_count = issue_kpis["overdue"]
        unassigned_issue_count = issue_kpis["unassigned"]
        resolved_recently = issue_kpis["resolved_recently"]
        planned = improvement_kpis["planned"]
        in_progress = improvement_kpis["in_progress"]
        completed = improvement_kpis["completed"]
        improvement_count = planned + in_progress
        activities = activity_bundle["activities"]
        last_updated = activity_bundle["last_updated"]
        from app.domains.business.activity.projection_flags import enrich_activities_for_viewer

        activities = await enrich_activities_for_viewer(
            self.session, moment_id, user_id, activities
        )
        _stage(timings, "members", t)
        _stage(timings, "vendors", t)
        _stage(timings, "approvals", t)
        _stage(timings, "issues", t)
        _stage(timings, "improvements", t)
        _stage(timings, "activity", t)

        t = time.perf_counter()
        ctx = OpsContext(
            moment=moment,
            moment_id=moment.moment_id,
            moment_type="BUSINESS_OPERATIONS",
            moment_name=moment.moment_name or "Operations",
            status=(moment.status or "draft"),
            is_active=(moment.status or "").lower() == "active",
            member_count=member_count,
            activity_count=len(activities),
            activities=activities,
            operating_currency=currency,
            operations_name=(ops_setup.operations_name if ops_setup else None) or moment.moment_name or "Operations",
            operations_scope=ops_setup.operations_scope if ops_setup else None,
            operating_model=(
                (ops_setup.operating_model_canonical if ops_setup else None)
                or (ops_setup.operating_model if ops_setup else None)
            ),
            owner_name=owner_name,
            last_updated=last_updated,
            monitoring_level=(governance.monitoring_level if governance else None),
            monthly_budget_minor=monthly_budget_minor or total_budget_minor,
            total_spend_minor=total_spend,
            total_budget_minor=total_budget_minor,
            remaining_minor=remaining,
            budget_usage_pct=usage,
            unallocated_minor=unallocated,
            allocations=allocations,
            over_budget_allocations=over_budget,
            vendor_count=vendor_count,
            critical_vendor_count=critical_vendor_count,
            vendor_due_by_name=vendor_due_by_name,
            pending_approvals=pending_approvals,
            overdue_approval_count=overdue_approval_count,
            approved_recently=approved_recently,
            rejected_recently=rejected_recently,
            amount_awaiting_minor=amount_awaiting,
            open_issue_count=open_issue_count,
            critical_issue_count=critical_issue_count,
            overdue_issue_count=overdue_issue_count,
            unassigned_issue_count=unassigned_issue_count,
            resolved_recently=resolved_recently,
            improvement_count=improvement_count,
            planned_improvement_count=planned,
            in_progress_improvement_count=in_progress,
            completed_improvement_count=completed,
            activated_at=str(moment.activated_at) if getattr(moment, "activated_at", None) else None,
            stage_timings_ms=timings,
            member_picker=member_picker,
        )
        ctx.projection = refresh_ops_projections(ctx)
        _stage(timings, "mapping", t)
        timings["Redis write"] = 0.0  # filled by cache layer when applicable
        ctx.stage_timings_ms = timings
        return ctx
