"""Load Future Building projection context in a single pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.personal.future_building.signals import FutureSignals, derive_future_signals
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalFutureBuildingProfile,
    PersonalMetricSnapshots,
    PersonalMomentHighlights,
    PersonalMomentTurningPoints,
    PersonalMoneyEvents,
    PersonalRuntimeSnapshots,
)
from app.domains.reference_data.catalog import get_reference_catalog

_FB = "FUTURE_BUILDING"


@dataclass
class FutureBuildingProjectionContext:
    user_id: UUID
    moment: MomentModel | None
    profile: PersonalFutureBuildingProfile | None = None
    runtime: PersonalRuntimeSnapshots | None = None
    metrics: list[PersonalMetricSnapshots] = field(default_factory=list)
    timeline: list[PersonalActivityTimeline] = field(default_factory=list)
    timeline_count: int = 0
    money_events: list[PersonalMoneyEvents] = field(default_factory=list)
    highlights: list[PersonalMomentHighlights] = field(default_factory=list)
    turning_points: list[PersonalMomentTurningPoints] = field(default_factory=list)
    signals: FutureSignals | None = None
    catalog: object = field(default_factory=get_reference_catalog)

    learning_count: int = 0
    milestone_count: int = 0
    opportunity_count: int = 0
    progress_count: int = 0


class FutureBuildingProjectionBuilder:
    @staticmethod
    async def build(
        session: AsyncSession,
        user_id: UUID,
        moment: MomentModel | None,
    ) -> FutureBuildingProjectionContext:
        if moment is None:
            return FutureBuildingProjectionContext(user_id=user_id, moment=None)

        moment_id = moment.id

        profile_result = await session.execute(
            select(PersonalFutureBuildingProfile).where(
                PersonalFutureBuildingProfile.moment_id == moment_id
            )
        )
        profile = profile_result.scalar_one_or_none()

        runtime_result = await session.execute(
            select(PersonalRuntimeSnapshots)
            .where(
                PersonalRuntimeSnapshots.moment_id == moment_id,
                PersonalRuntimeSnapshots.moment_type_code == _FB,
            )
            .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
            .limit(1)
        )
        runtime = runtime_result.scalar_one_or_none()

        metrics_result = await session.execute(
            select(PersonalMetricSnapshots)
            .where(
                PersonalMetricSnapshots.moment_id == moment_id,
                PersonalMetricSnapshots.moment_type_code == _FB,
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

        learning_count = sum(
            1 for t in timeline if (t.event_type or "").upper() == "LEARNING"
        )
        milestone_count = sum(
            1 for t in timeline if (t.event_type or "").upper() == "MILESTONE"
        )
        opportunity_count = sum(
            1 for t in timeline if (t.event_type or "").upper() == "OPPORTUNITY"
        )
        progress_count = sum(
            1 for t in timeline if (t.event_type or "").upper() == "PROGRESS"
        )

        signals = derive_future_signals(
            runtime=runtime,
            metrics=metrics,
            profile=profile,
            timeline_count=timeline_count,
            learning_count=learning_count,
            milestone_count=milestone_count,
            opportunity_count=opportunity_count,
        )

        return FutureBuildingProjectionContext(
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
            learning_count=learning_count,
            milestone_count=milestone_count,
            opportunity_count=opportunity_count,
            progress_count=progress_count,
        )
