"""Operations template builder — one-pass OpsContext from SQL."""
from __future__ import annotations

import time
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        members = await self.session.execute(
            select(BusinessMomentMembers).where(
                BusinessMomentMembers.moment_id == moment_id,
                BusinessMomentMembers.member_status.in_(["active", "configured"]),
            )
        )
        member_rows = list(members.scalars().all())
        member_count = len(member_rows)
        member_picker = [
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
        owner_name = (owner.name if owner else None) or (str(owner.user_id) if owner and owner.user_id else None)
        _stage(timings, "members", t)

        t = time.perf_counter()
        # spend already loaded
        _stage(timings, "spend", t)

        t = time.perf_counter()
        vendor_q = await self.session.execute(
            select(OperationsVendorUpdates).where(
                OperationsVendorUpdates.moment_id == moment_id,
                OperationsVendorUpdates.is_voided.is_(False),
            )
        )
        vendor_rows = list(vendor_q.scalars().all())
        vendor_count = len(vendor_rows)
        critical_vendor_count = sum(
            1
            for v in vendor_rows
            if (getattr(v, "impact_level", None) or getattr(v, "priority", None) or "").lower()
            in {"critical", "high"}
        )
        _stage(timings, "vendors", t)

        t = time.perf_counter()
        today = date.today()
        recent_cut = datetime.now(timezone.utc) - timedelta(days=14)
        approval_q = await self.session.execute(
            select(OperationsApprovalRequests).where(
                OperationsApprovalRequests.moment_id == moment_id,
                OperationsApprovalRequests.is_voided.is_(False),
            )
        )
        approval_rows = list(approval_q.scalars().all())
        pending_approvals = sum(1 for a in approval_rows if (a.approval_status or "") == "pending")
        overdue_approval_count = sum(
            1
            for a in approval_rows
            if (a.approval_status or "") == "pending"
            and getattr(a, "due_date", None) is not None
            and a.due_date < today
        )
        approved_recently = sum(
            1
            for a in approval_rows
            if (a.approval_status or "") == "approved"
            and a.updated_at
            and (
                a.updated_at.replace(tzinfo=timezone.utc)
                if a.updated_at.tzinfo is None
                else a.updated_at
            )
            >= recent_cut
        )
        rejected_recently = sum(
            1
            for a in approval_rows
            if (a.approval_status or "") == "rejected"
            and a.updated_at
            and (
                a.updated_at.replace(tzinfo=timezone.utc)
                if a.updated_at.tzinfo is None
                else a.updated_at
            )
            >= recent_cut
        )
        awaiting_amounts = [
            int(a.amount_minor)
            for a in approval_rows
            if (a.approval_status or "") == "pending" and a.amount_minor is not None
        ]
        amount_awaiting = sum(awaiting_amounts) if awaiting_amounts else None
        _stage(timings, "approvals", t)

        t = time.perf_counter()
        issue_q = await self.session.execute(
            select(OperationsIssues).where(
                OperationsIssues.moment_id == moment_id,
                OperationsIssues.is_voided.is_(False),
            )
        )
        issue_rows = list(issue_q.scalars().all())
        open_statuses = {"open", "investigating"}
        open_issues = [i for i in issue_rows if (i.issue_status or "") in open_statuses]
        open_issue_count = len(open_issues)
        critical_issue_count = sum(1 for i in open_issues if (i.severity or "").lower() == "critical")
        overdue_issue_count = sum(
            1
            for i in open_issues
            if i.target_resolution_date is not None and i.target_resolution_date < today
        )
        unassigned_issue_count = sum(1 for i in open_issues if i.owner_id is None)
        resolved_recently = sum(
            1
            for i in issue_rows
            if (i.issue_status or "") == "resolved"
            and i.resolved_at
            and i.resolved_at.replace(tzinfo=timezone.utc) >= recent_cut
        )
        _stage(timings, "issues", t)

        t = time.perf_counter()
        improvement_q = await self.session.execute(
            select(OperationsImprovements).where(
                OperationsImprovements.moment_id == moment_id,
                OperationsImprovements.is_voided.is_(False),
            )
        )
        improvement_rows = list(improvement_q.scalars().all())
        planned = sum(
            1 for i in improvement_rows if (i.improvement_status or "") in {"recorded", "planned"}
        )
        in_progress = sum(
            1 for i in improvement_rows if (i.improvement_status or "") in {"in_follow_up", "in_progress"}
        )
        completed = sum(
            1 for i in improvement_rows if (i.improvement_status or "") in {"completed", "done"}
        )
        improvement_count = planned + in_progress
        _stage(timings, "improvements", t)

        t = time.perf_counter()
        events = await self.session.execute(
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
            }
            for e in activity_rows
        ]
        last_updated = str(activity_rows[0].occurred_at) if activity_rows else None
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
