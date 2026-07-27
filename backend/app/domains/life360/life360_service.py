"""Life360 service.

Refresh delegates entirely to the existing SQL procedure
``sp_refresh_life360_snapshots(p_user_id)`` which recomputes and upserts the
``life360_snapshots`` row for the day. All read/analytics/summary methods only
SELECT from that snapshot table -- no scores are recomputed in Python (no
duplicate calculations).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domains.life360.api_schemas import (
    Life360AnalyticsResponse,
    Life360DimensionStat,
    Life360EnergyAllocation,
    Life360RefreshResponse,
    Life360SummaryResponse,
    Life360TrendPoint,
)
from app.domains.life360.models import Life360Snapshots
from app.domains.life360.repository import Life360SnapshotsRepository
from app.domains.life360.schemas import Life360SnapshotsSchema

logger = logging.getLogger(__name__)

_PERSONAL_BOOTSTRAP_PROCS: tuple[str, ...] = (
    "sp_refresh_personal_life_health",
    "sp_refresh_personal_life_dimensions",
    "sp_refresh_personal_life_snapshot",
)
_REFRESH_SQL = text("CALL sp_refresh_life360_snapshots((:uid)::uuid)")
_NO_SNAPSHOT = "No Life360 snapshot yet. Trigger a refresh first."
_EMPTY_CONFIDENCE_THRESHOLD = 25


class Life360Service:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.snapshots_repo = Life360SnapshotsRepository(session)

    async def _latest(self, user_id: UUID) -> Life360Snapshots | None:
        rows = await self.snapshots_repo.list(filters={"user_id": user_id}, order_by="-snapshot_date", limit=1)
        return rows[0] if rows else None

    async def _require_latest(self, user_id: UUID) -> Life360Snapshots:
        latest = await self._latest(user_id)
        if latest is None:
            raise NotFoundError(_NO_SNAPSHOT)
        return latest

    @staticmethod
    def _confidence_score(snapshot: Life360Snapshots | None) -> float:
        if snapshot is None or snapshot.signal_confidence_score is None:
            return 0.0
        return float(snapshot.signal_confidence_score)

    @classmethod
    def _is_full_state(cls, snapshot: Life360Snapshots | None) -> bool:
        return cls._confidence_score(snapshot) >= _EMPTY_CONFIDENCE_THRESHOLD

    async def home(self, user_id: UUID) -> dict[str, object]:
        latest = await self._latest(user_id)
        state = "FULL" if self._is_full_state(latest) else "EMPTY"
        return {
            "state": state,
            "counts": {
                "personal_signals": 1 if latest and latest.personal_score is not None else 0,
                "group_signals": 1 if latest and latest.group_score is not None else 0,
                "business_signals": 1 if latest and latest.business_score is not None else 0,
            },
        }

    async def _bootstrap_personal_sources(self, user_id: UUID) -> None:
        """Refresh personal health → dimensions → aggregate before Life360 rollup."""
        uid = {"uid": str(user_id)}
        for proc in _PERSONAL_BOOTSTRAP_PROCS:
            try:
                async with self.session.begin_nested():
                    await self.session.execute(
                        text(f"CALL {proc}((:uid)::uuid)"), uid
                    )
            except Exception:
                logger.exception(
                    "Life360 personal bootstrap failed on %s for user=%s",
                    proc,
                    user_id,
                )
    # ------------------------------- refresh ------------------------------- #
    async def refresh(self, user_id: UUID, *, force: bool = False) -> Life360RefreshResponse:
        latest = await self._latest(user_id)
        if not force and latest is not None and latest.updated_at is not None:
            updated = latest.updated_at
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            age_s = (datetime.now(timezone.utc) - updated).total_seconds()
            if age_s < 60:
                return Life360RefreshResponse(
                    refreshed=False,
                    snapshot=Life360SnapshotsSchema.model_validate(latest),
                )
        await self._bootstrap_personal_sources(user_id)
        await self.session.execute(_REFRESH_SQL, {"uid": str(user_id)})
        await self.session.commit()
        latest = await self._latest(user_id)
        return Life360RefreshResponse(
            refreshed=True,
            snapshot=Life360SnapshotsSchema.model_validate(latest) if latest else None,
        )

    # -------------------------------- read --------------------------------- #
    async def read(self, user_id: UUID) -> Life360SnapshotsSchema:
        latest = await self._require_latest(user_id)
        return Life360SnapshotsSchema.model_validate(latest)

    # ------------------------------ analytics ------------------------------ #
    async def analytics(self, user_id: UUID, *, trend_limit: int = 12) -> Life360AnalyticsResponse:
        latest = await self._require_latest(user_id)
        history = await self.snapshots_repo.list(
            filters={"user_id": user_id}, order_by="-snapshot_date", limit=trend_limit
        )
        trend = [
            Life360TrendPoint(snapshot_date=s.snapshot_date, life_alignment_score=s.life_alignment_score)
            for s in reversed(history)
        ]
        return Life360AnalyticsResponse(
            snapshot_date=latest.snapshot_date,
            life_alignment_score=latest.life_alignment_score,
            signal_confidence_score=latest.signal_confidence_score,
            momentum_score=latest.momentum_score,
            momentum_status=latest.momentum_status,
            strongest_driver=latest.strongest_driver,
            biggest_tension=latest.biggest_tension,
            dimensions=[
                Life360DimensionStat(dimension="money", score=latest.money_score, status=latest.money_status),
                Life360DimensionStat(dimension="relationship", score=latest.relationship_score, status=latest.relationship_status),
                Life360DimensionStat(dimension="execution", score=latest.execution_score, status=latest.execution_status),
                Life360DimensionStat(dimension="growth", score=latest.growth_score, status=latest.growth_status),
            ],
            energy=Life360EnergyAllocation(
                personal_pct=latest.personal_energy_pct,
                group_pct=latest.group_energy_pct,
                business_pct=latest.business_energy_pct,
            ),
            domain_scores={
                "personal": latest.personal_score,
                "group": latest.group_score,
                "business": latest.business_score,
            },
            trend=trend,
        )

    # ------------------------------- summary ------------------------------- #
    async def summary(self, user_id: UUID) -> Life360SummaryResponse:
        latest = await self._require_latest(user_id)
        return Life360SummaryResponse(
            snapshot_date=latest.snapshot_date,
            life_alignment_score=latest.life_alignment_score,
            life_phase=latest.life_phase,
            momentum_score=latest.momentum_score,
            momentum_status=latest.momentum_status,
            strongest_driver=latest.strongest_driver,
            biggest_tension=latest.biggest_tension,
            reflection_summary=latest.reflection_summary,
            active_dimensions_count=latest.active_dimensions_count,
        )
