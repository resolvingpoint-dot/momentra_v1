"""Circle service.

Refresh delegates entirely to the existing SQL procedure ``sp_refresh_circle``
(which orchestrates ``sp_refresh_circle_participants`` /
``sp_refresh_circle_participant_stats`` / ``sp_refresh_circle_suggestions``).
Read/analytics/summary only read from the circle snapshot tables and order/count
them by the precomputed ``rank_order`` / ``participation_score`` -- no scores are
recomputed in Python.
"""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.circle.api_schemas import (
    CircleAnalyticsResponse,
    CircleParticipantEntry,
    CircleReadResponse,
    CircleRecentActivityItem,
    CircleSummaryResponse,
    CircleTopParticipant,
    CircleRefreshResponse,
)
from app.domains.circle.repository import (
    CircleParticipantsRepository,
    CircleParticipantStatsRepository,
    CircleSuggestionsRepository,
)
from app.domains.circle.schemas import (
    CircleParticipantsSchema,
    CircleParticipantStatsSchema,
    CircleSuggestionsSchema,
)

logger = logging.getLogger(__name__)

_REFRESH_SQL = text("CALL sp_refresh_circle((:uid)::uuid)")
_RANK_SENTINEL = 10**9
_SOURCE_FLAGS_SQL = text(
    """
    SELECT
        circle_participant_id,
        BOOL_OR(source_type = 'GROUP') AS is_group_participant,
        BOOL_OR(source_type = 'BUSINESS') AS is_business_participant
    FROM circle_participant_sources
    WHERE user_id = (:uid)::uuid
    GROUP BY circle_participant_id
    """
)
_RECENT_ACTIVITY_SQL = text(
    """
    SELECT
        source_type,
        source_moment_id,
        source_moment_name,
        source_moment_type,
        COUNT(DISTINCT circle_participant_id)::int AS participant_count,
        MAX(participation_date) AS last_activity_date
    FROM circle_participant_sources
    WHERE user_id = (:uid)::uuid
    GROUP BY
        source_type,
        source_moment_id,
        source_moment_name,
        source_moment_type
    ORDER BY MAX(participation_date) DESC NULLS LAST
    LIMIT :lim
    """
)


class CircleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.participants_repo = CircleParticipantsRepository(session)
        self.stats_repo = CircleParticipantStatsRepository(session)
        self.suggestions_repo = CircleSuggestionsRepository(session)

    # ------------------------------- refresh ------------------------------- #
    async def refresh(self, user_id: UUID) -> CircleRefreshResponse:
        refreshed = False
        try:
            async with self.session.begin_nested():
                await self.session.execute(_REFRESH_SQL, {"uid": str(user_id)})
            refreshed = True
        except Exception:
            logger.exception(
                "Circle refresh failed for user=%s; returning snapshot counts",
                user_id,
            )

        return CircleRefreshResponse(
            refreshed=refreshed,
            participant_count=await self.participants_repo.count(
                filters={"user_id": user_id}, include_deleted=True
            ),
            suggestion_count=await self.suggestions_repo.count(
                filters={"user_id": user_id, "is_active": True}
            ),
        )

    async def _entries(self, user_id: UUID) -> list[tuple]:
        """Participants paired with their stats, ordered by the precomputed rank.

        ``is_active`` on circle_participants is a product flag (Active filter), not
        a soft-delete marker — include inactive rows so Circle updated can render.
        """
        participants = await self.participants_repo.list(
            filters={"user_id": user_id},
            limit=None,
            include_deleted=True,
        )
        if not participants:
            return []
        pids = [p.circle_participant_id for p in participants]
        stats = await self.stats_repo.list(filters={"circle_participant_id__in": pids}, limit=None)
        stats_by_pid = {s.circle_participant_id: s for s in stats}
        entries = [(p, stats_by_pid.get(p.circle_participant_id)) for p in participants]
        entries.sort(
            key=lambda e: (
                e[1].rank_order if e[1] is not None and e[1].rank_order is not None else _RANK_SENTINEL,
                e[0].participant_name,
            )
        )
        return entries

    @staticmethod
    def _top(participant, stats) -> CircleTopParticipant:
        return CircleTopParticipant(
            circle_participant_id=participant.circle_participant_id,
            participant_name=participant.participant_name,
            participation_score=stats.participation_score if stats else None,
            shared_moment_count=stats.shared_moment_count if stats else None,
            active_moment_count=stats.active_moment_count if stats else None,
            rank_order=stats.rank_order if stats else None,
        )

    async def _source_flags(self, user_id: UUID) -> dict[UUID, tuple[bool, bool]]:
        result = await self.session.execute(_SOURCE_FLAGS_SQL, {"uid": str(user_id)})
        flags: dict[UUID, tuple[bool, bool]] = {}
        for row in result.mappings():
            flags[row["circle_participant_id"]] = (
                bool(row["is_group_participant"]),
                bool(row["is_business_participant"]),
            )
        return flags

    async def _recent_activity(
        self, user_id: UUID, *, limit: int = 12
    ) -> list[CircleRecentActivityItem]:
        result = await self.session.execute(
            _RECENT_ACTIVITY_SQL,
            {"uid": str(user_id), "lim": limit},
        )
        return [
            CircleRecentActivityItem(
                source_type=row["source_type"],
                source_moment_id=row["source_moment_id"],
                source_moment_name=row["source_moment_name"],
                source_moment_type=row["source_moment_type"],
                participant_count=int(row["participant_count"] or 0),
                last_activity_date=row["last_activity_date"],
            )
            for row in result.mappings()
        ]

    # -------------------------------- read --------------------------------- #
    async def read(self, user_id: UUID) -> CircleReadResponse:
        entries = await self._entries(user_id)
        suggestions = await self.suggestions_repo.list(
            filters={"user_id": user_id, "is_active": True}, order_by="-confidence_score", limit=None
        )
        flags = await self._source_flags(user_id)
        recent = await self._recent_activity(user_id)
        return CircleReadResponse(
            participants=[
                CircleParticipantEntry(
                    participant=CircleParticipantsSchema.model_validate(p),
                    stats=CircleParticipantStatsSchema.model_validate(s) if s else None,
                    is_group_participant=flags.get(p.circle_participant_id, (False, False))[0],
                    is_business_participant=flags.get(p.circle_participant_id, (False, False))[1],
                )
                for p, s in entries
            ],
            suggestions=[CircleSuggestionsSchema.model_validate(x) for x in suggestions],
            recent_activity=recent,
        )

    # ------------------------------ analytics ------------------------------ #
    async def analytics(self, user_id: UUID, *, top_limit: int = 10) -> CircleAnalyticsResponse:
        entries = await self._entries(user_id)
        return CircleAnalyticsResponse(
            total_participants=await self.participants_repo.count(
                filters={"user_id": user_id}, include_deleted=True
            ),
            active_participants=await self.participants_repo.count(
                filters={"user_id": user_id, "is_active": True}, include_deleted=True
            ),
            suggestion_count=await self.suggestions_repo.count(filters={"user_id": user_id, "is_active": True}),
            top_participants=[self._top(p, s) for p, s in entries[:top_limit]],
        )

    # ------------------------------- summary ------------------------------- #
    async def summary(self, user_id: UUID) -> CircleSummaryResponse:
        entries = await self._entries(user_id)
        top = self._top(*entries[0]) if entries else None
        return CircleSummaryResponse(
            participant_count=await self.participants_repo.count(
                filters={"user_id": user_id}, include_deleted=True
            ),
            active_participant_count=await self.participants_repo.count(
                filters={"user_id": user_id, "is_active": True}, include_deleted=True
            ),
            suggestion_count=await self.suggestions_repo.count(filters={"user_id": user_id, "is_active": True}),
            top_participant=top,
        )
