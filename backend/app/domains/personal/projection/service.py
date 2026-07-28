"""Orchestrate projection build, cache, and tab slices."""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache as core_cache
from app.core.errors import SnapshotRebuildingError
from app.core.request_context import set_build_coalesced, set_cache_hit, set_projection_build_ms
from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import PERSONAL_CONTEXT, normalize_moment_type_code
from app.domains.personal.projection.builder import ProjectionBuilder
from app.domains.personal.projection.cache import (
    CachedProjection,
    current_version,
    get_cached,
    invalidate_projection_cache,
    set_cached,
)
from app.domains.personal.projection.mappers.life_projection import build_life_projection
from app.domains.personal.projection.mappers.memory_projection import (
    build_memory_projection as map_memory_projection,
)
from app.domains.personal.projection.mappers.moment_projection import build_moment_projection
from app.domains.personal.projection.redis_slice_cache import get_slice, set_slice

_ACTIVE = {"ACTIVE"}
_inflight: dict[UUID, asyncio.Task[CachedProjection]] = {}
_LOCK_MISS_POLLS = 300
_LOCK_MISS_SLEEP = 0.05


class ProjectionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _build_and_cache(self, user_id: UUID) -> CachedProjection:
        start = time.perf_counter()
        lock_key = f"projection_build:{user_id}"
        acquired = await core_cache.acquire_lock(lock_key, ttl=30)
        try:
            cached = get_cached(user_id)
            if cached is not None:
                set_build_coalesced(True)
                return cached
            if not acquired:
                # Another worker holds the build lock. Poll cache only —
                # never await _inflight[user_id] here: this coroutine may
                # already *be* that inflight task (self-await RuntimeError).
                for _ in range(_LOCK_MISS_POLLS):
                    cached = get_cached(user_id)
                    if cached is not None:
                        set_build_coalesced(True)
                        return cached
                    await asyncio.sleep(_LOCK_MISS_SLEEP)
                raise SnapshotRebuildingError(
                    "Personal snapshot is rebuilding; retry shortly"
                )
            ctx = await ProjectionBuilder.build(self.session, user_id)
            version = max(1, current_version(user_id))
            cached = CachedProjection(
                version=version,
                generated_at=datetime.now(timezone.utc),
                context=ctx,
            )
            set_cached(user_id, cached)
            set_projection_build_ms((time.perf_counter() - start) * 1000)
            return cached
        finally:
            if acquired:
                await core_cache.release_lock(lock_key)

    async def get_cached_context(
        self, user_id: UUID, *, force_refresh: bool = False
    ) -> CachedProjection:
        if force_refresh:
            invalidate_projection_cache(user_id)
        cached = get_cached(user_id)
        if cached is not None:
            return cached
        if user_id in _inflight:
            set_build_coalesced(True)
            return await _inflight[user_id]
        task = asyncio.create_task(self._build_and_cache(user_id))
        _inflight[user_id] = task
        try:
            return await task
        finally:
            _inflight.pop(user_id, None)

    async def _active_moment_count(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(MomentModel)
            .where(
                MomentModel.user_id == user_id,
                MomentModel.context_type == PERSONAL_CONTEXT,
                MomentModel.status == "ACTIVE",
            )
        )
        return int(result.scalar_one() or 0)

    async def _context_for_slice(
        self, user_id: UUID, *, force_refresh: bool = False
    ) -> CachedProjection:
        """Return cached context; cheap count check instead of full rebuild."""
        cached = await self.get_cached_context(user_id, force_refresh=force_refresh)
        if force_refresh:
            return cached
        active_count = await self._active_moment_count(user_id)
        if active_count != len(cached.context.active_moments):
            return await self.get_cached_context(user_id, force_refresh=True)
        return cached

    def envelope(self, cached: CachedProjection) -> dict[str, Any]:
        return {
            "projection_version": cached.version,
            "generated_at": cached.generated_at.isoformat(),
        }

    async def moment_slice(
        self,
        user_id: UUID,
        moment: MomentModel | None,
        moment_type_code: str,
        *,
        accounts_summary: dict[str, Any],
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(moment_type_code)

        if code == "FUTURE_BUILDING":
            from app.domains.personal.templates.future_building.moments_mapper import (
                build_future_building_moments,
            )
            from app.domains.personal.templates.future_building.projection_builder import (
                FutureBuildingProjectionBuilder,
            )

            ctx = await FutureBuildingProjectionBuilder.build(
                self.session, user_id, moment
            )
            base = build_future_building_moments(ctx, accounts_summary=accounts_summary)
        else:
            from app.domains.personal.life_operations.moments_mapper import (
                build_moments_projection,
            )

            base = await build_moments_projection(
                self.session, user_id, moment, accounts_summary=accounts_summary
            )

        if not force_refresh:
            cached_slice = await get_slice(user_id, code, "moments")
            if cached_slice is not None:
                set_cache_hit(True)
                return cached_slice

        cached = await self._context_for_slice(user_id, force_refresh=force_refresh)
        projection = None
        if moment is not None and moment.status in _ACTIVE:
            if code == "FUTURE_BUILDING":
                projection = base.get("moment_projection")
            else:
                projection = build_moment_projection(cached.context, code)
            if projection is None and not force_refresh:
                cached = await self._context_for_slice(user_id, force_refresh=True)
                if code != "FUTURE_BUILDING":
                    projection = build_moment_projection(cached.context, code)
        result = {**self.envelope(cached), **base, "moment_projection": projection}
        await set_slice(user_id, code, "moments", result)
        return result

    async def memory_slice(
        self,
        user_id: UUID,
        moment: MomentModel | None,
        moment_type_code: str,
        *,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(moment_type_code)

        if not force_refresh:
            cached_slice = await get_slice(user_id, code, "memory")
            if cached_slice is not None:
                set_cache_hit(True)
                return cached_slice

        cached = await self._context_for_slice(user_id, force_refresh=force_refresh)

        if moment is None:
            status = "EMPTY"
        elif moment.status in _ACTIVE:
            status = "ACTIVE"
        else:
            status = "SETUP"

        memory_projection = None
        if status == "ACTIVE":
            memory_projection = map_memory_projection(cached.context, code)
            if memory_projection is None and not force_refresh:
                cached = await self._context_for_slice(user_id, force_refresh=True)
                memory_projection = map_memory_projection(cached.context, code)

        result = {
            **self.envelope(cached),
            "moment_type_code": code,
            "status": status,
            "memory_projection": memory_projection,
        }
        from app.core.request_context import set_projection_version

        set_projection_version(cached.version)
        await set_slice(user_id, code, "memory", result)
        return result

    async def life_slice(
        self, user_id: UUID, *, force_refresh: bool = False
    ) -> dict[str, Any]:
        if not force_refresh:
            cached_slice = await get_slice(user_id, "PERSONAL", "life")
            if cached_slice is not None:
                set_cache_hit(True)
                return cached_slice

        cached = await self._context_for_slice(user_id, force_refresh=force_refresh)
        active_count = len(cached.context.active_moments)
        is_empty = active_count == 0
        projection = None if is_empty else build_life_projection(cached.context)
        result = {
            **self.envelope(cached),
            "active_moment_count": active_count,
            "is_empty": is_empty,
            "date_range_label": datetime.now(timezone.utc).strftime("%B %Y"),
            "life_projection": projection,
            "metrics": projection,
        }
        await set_slice(user_id, "PERSONAL", "life", result)
        return result
