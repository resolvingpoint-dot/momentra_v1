"""Load Relationships projection context in a single pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalMetricSnapshots,
    PersonalMomentHighlights,
    PersonalMomentTurningPoints,
    PersonalMoneyEvents,
    PersonalRelationshipsProfile,
    PersonalRuntimeSnapshots,
)
from app.domains.personal.templates.relationships.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.relationships.signals import (
    RelationshipsSignals,
    derive_relationships_signals,
)
from app.domains.reference_data.catalog import get_reference_catalog

_RS = MOMENT_TYPE_CODE


@dataclass
class RelationshipsProjectionContext:
    user_id: UUID
    moment: MomentModel | None
    profile: PersonalRelationshipsProfile | None = None
    runtime: PersonalRuntimeSnapshots | None = None
    metrics: list[PersonalMetricSnapshots] = field(default_factory=list)
    timeline: list[PersonalActivityTimeline] = field(default_factory=list)
    timeline_count: int = 0
    money_events: list[PersonalMoneyEvents] = field(default_factory=list)
    highlights: list[PersonalMomentHighlights] = field(default_factory=list)
    turning_points: list[PersonalMomentTurningPoints] = field(default_factory=list)
    signals: RelationshipsSignals | None = None
    catalog: object = field(default_factory=get_reference_catalog)

    connection_count: int = 0
    support_count: int = 0
    experience_count: int = 0
    investment_count: int = 0
    adjust_count: int = 0


class RelationshipsProjectionBuilder:
    @staticmethod
    async def build(
        session: AsyncSession,
        user_id: UUID,
        moment: MomentModel | None,
    ) -> RelationshipsProjectionContext:
        if moment is None:
            return RelationshipsProjectionContext(user_id=user_id, moment=None)

        moment_id = moment.id

        profile_result = await session.execute(
            select(PersonalRelationshipsProfile).where(
                PersonalRelationshipsProfile.moment_id == moment_id
            )
        )
        profile = profile_result.scalar_one_or_none()

        runtime_result = await session.execute(
            select(PersonalRuntimeSnapshots)
            .where(
                PersonalRuntimeSnapshots.moment_id == moment_id,
                PersonalRuntimeSnapshots.moment_type_code == _RS,
            )
            .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
            .limit(1)
        )
        runtime = runtime_result.scalar_one_or_none()

        metrics_result = await session.execute(
            select(PersonalMetricSnapshots)
            .where(
                PersonalMetricSnapshots.moment_id == moment_id,
                PersonalMetricSnapshots.moment_type_code == _RS,
            )
            .order_by(PersonalMetricSnapshots.snapshot_date.desc())
            .limit(10)
        )
        metrics = list(metrics_result.scalars().all())

        timeline_result = await session.execute(
            select(PersonalActivityTimeline)
            .where(
                PersonalActivityTimeline.moment_id == moment_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
            .order_by(PersonalActivityTimeline.event_occurred_at.desc())
            .limit(50)
        )
        timeline = list(timeline_result.scalars().all())

        count_result = await session.execute(
            select(func.count())
            .select_from(PersonalActivityTimeline)
            .where(
                PersonalActivityTimeline.moment_id == moment_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
        )
        timeline_count = int(count_result.scalar_one() or 0)

        money_result = await session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.moment_id == moment_id,
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        money_events = list(money_result.scalars().all())

        highlights_result = await session.execute(
            select(PersonalMomentHighlights)
            .where(
                PersonalMomentHighlights.moment_id == moment_id,
                PersonalMomentHighlights.is_current.is_(True),
            )
            .order_by(PersonalMomentHighlights.occurred_at.desc())
            .limit(6)
        )
        highlights = list(highlights_result.scalars().all())

        turning_result = await session.execute(
            select(PersonalMomentTurningPoints)
            .where(
                PersonalMomentTurningPoints.moment_id == moment_id,
                PersonalMomentTurningPoints.is_current.is_(True),
            )
            .order_by(PersonalMomentTurningPoints.occurred_at.desc().nullslast())
            .limit(6)
        )
        turning_points = list(turning_result.scalars().all())

        def _count(event_type: str) -> int:
            return sum(
                1 for t in timeline if (t.event_type or "").upper() == event_type
            )

        connection_count = _count("CONNECTION")
        support_count = _count("SUPPORT")
        experience_count = _count("SHARED_EXPERIENCE")
        investment_count = _count("RELATIONSHIP_INVESTMENT")
        adjust_count = _count("ADJUST") + _count("RELATIONSHIP_ADJUST")

        signals = derive_relationships_signals(
            runtime=runtime,
            metrics=metrics,
            profile=profile,
            timeline_count=timeline_count,
            connection_count=connection_count,
            support_count=support_count,
            experience_count=experience_count,
            investment_count=investment_count,
            adjust_count=adjust_count,
        )

        return RelationshipsProjectionContext(
            user_id=user_id,
            moment=moment,
            profile=profile,
            runtime=runtime,
            metrics=metrics,
            timeline=timeline,
            timeline_count=timeline_count,
            money_events=money_events,
            highlights=highlights,
            turning_points=turning_points,
            signals=signals,
            connection_count=connection_count,
            support_count=support_count,
            experience_count=experience_count,
            investment_count=investment_count,
            adjust_count=adjust_count,
        )
