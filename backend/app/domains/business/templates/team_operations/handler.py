"""Team Operations template builder — builds TeamOpsContext from SQL."""
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
    TeamApprovalRequests,
    TeamEscalations,
    TeamIssueRisks,
    TeamMeetings,
    TeamParticipation,
    TeamRecognitions,
)
from app.domains.business.templates.team_operations.context import TeamOpsContext


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


async def _count_open_issues(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(TeamIssueRisks)
        .where(
            TeamIssueRisks.moment_id == moment_id,
            TeamIssueRisks.resolution_status.in_(("open", "investigating")),
            TeamIssueRisks.is_voided.is_(False),
        )
    )
    return int(result.scalar() or 0)


async def _count_pending_approvals(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(TeamApprovalRequests)
        .where(
            TeamApprovalRequests.moment_id == moment_id,
            TeamApprovalRequests.approval_status == "pending",
            TeamApprovalRequests.is_voided.is_(False),
        )
    )
    return int(result.scalar() or 0)


async def _count_recognitions(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(TeamRecognitions)
        .where(
            TeamRecognitions.moment_id == moment_id,
            TeamRecognitions.is_voided.is_(False),
        )
    )
    return int(result.scalar() or 0)


async def _count_meetings(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(TeamMeetings)
        .where(
            TeamMeetings.moment_id == moment_id,
            TeamMeetings.is_voided.is_(False),
        )
    )
    return int(result.scalar() or 0)


async def _count_escalations(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(TeamEscalations)
        .where(
            TeamEscalations.moment_id == moment_id,
            TeamEscalations.status == "open",
            TeamEscalations.is_voided.is_(False),
        )
    )
    return int(result.scalar() or 0)


async def _count_participation(session: AsyncSession, moment_id: UUID) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(TeamParticipation)
        .where(
            TeamParticipation.moment_id == moment_id,
            TeamParticipation.is_voided.is_(False),
        )
    )
    return int(result.scalar() or 0)


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
            "created_by": str(e.created_by) if e.created_by else None,
        }
        for e in activity_rows
    ]
    total = await session.execute(
        select(func.count())
        .select_from(BusinessActivityEvents)
        .where(
            BusinessActivityEvents.business_moment_id == moment_id,
            BusinessActivityEvents.is_voided.is_(False),
        )
    )
    return {
        "activities": activities,
        "activity_count": int(total.scalar() or 0),
    }


async def _load_team_sections_concurrent(moment_id: UUID) -> tuple:
    return await asyncio.gather(
        _with_session(lambda s: _count_members(s, moment_id)),
        _with_session(lambda s: _count_open_issues(s, moment_id)),
        _with_session(lambda s: _count_pending_approvals(s, moment_id)),
        _with_session(lambda s: _count_recognitions(s, moment_id)),
        _with_session(lambda s: _count_meetings(s, moment_id)),
        _with_session(lambda s: _count_escalations(s, moment_id)),
        _with_session(lambda s: _count_participation(s, moment_id)),
        _with_session(lambda s: _load_activity(s, moment_id)),
    )


class TeamOpsTemplateBuilder:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build(
        self, user_id: UUID, moment_id: UUID, *, with_projection: bool = True
    ) -> TeamOpsContext:
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

        (
            member_count,
            open_issues,
            pending_approvals,
            recognition_count,
            meeting_count,
            escalation_count,
            participation_count,
            activity_bundle,
        ) = await _load_team_sections_concurrent(moment_id)

        from app.domains.business.activity.projection_flags import enrich_activities_for_viewer

        activities = await enrich_activities_for_viewer(
            self.session,
            moment_id,
            user_id,
            activity_bundle["activities"],
        )

        ctx = TeamOpsContext(
            moment=moment,
            moment_id=moment.moment_id,
            moment_type="TEAM_OPERATIONS",
            moment_name=moment.moment_name or "Team",
            status=(moment.status or "draft"),
            is_active=(moment.status or "").lower() == "active",
            member_count=member_count,
            activity_count=activity_bundle["activity_count"],
            activities=activities,
            team_name=(setup.team_name if setup else None) or moment.moment_name or "",
            operating_currency=(setup.currency if setup else None) or "INR",
            monthly_budget_minor=setup.monthly_budget_minor if setup else None,
            open_issues=open_issues,
            pending_approvals=pending_approvals,
            recognition_count=recognition_count,
            meeting_count=meeting_count,
            escalation_count=escalation_count,
            participation_count=participation_count,
        )
        from app.domains.business.templates.team_operations.projector import (
            refresh_team_ops_projections,
        )

        if with_projection:
            # In-memory only — Redis is SoT for HTTP reads (no SQL persist on request path).
            ctx.projection = await refresh_team_ops_projections(
                self.session, ctx, persist=False
            )
        return ctx
