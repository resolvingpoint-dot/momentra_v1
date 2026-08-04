"""BusinessActiveService — cache-first projection reads + activity CRUD + life/memory."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.service import BusinessActivityService
from app.domains.business.life.builder import build_life
from app.domains.business.memory.builder import build_memory
from app.domains.business.models import BusinessMoments
from app.domains.business.permissions import require_moment_read_access
from app.domains.business.projection_cache import MOMENT_SLICES, set_cached_slice
from app.domains.business.projection_read import cached_or_build, cached_or_build_user_agg
from app.domains.business.templates.registry import builders_for
from app.domains.projections import projection_cache


class BusinessActiveService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.activity = BusinessActivityService(session)

    async def _moment_type(self, moment_id: UUID) -> str:
        result = await self.session.execute(
            select(BusinessMoments.moment_type).where(BusinessMoments.moment_id == moment_id)
        )
        row = result.scalar_one_or_none()
        return (row or "TEAM_OPERATIONS").upper()

    async def _build_all_moment_slices(
        self, user_id: UUID, moment_id: UUID, moment_type: str
    ) -> dict[str, dict]:
        """One template build → pulse + moments + quick_add (Personal-like coalesce).

        Writes Redis once per slice. Caller must hold the frozen ``_bundle`` lock.
        """
        import time

        builders = builders_for(moment_type, self.session)
        if builders is None:
            return {}
        t_ctx = time.perf_counter()
        ctx = await builders["build"](user_id, moment_id)
        context_ms = (time.perf_counter() - t_ctx) * 1000
        payloads: dict[str, dict] = {}
        map_ms = 0.0
        write_ms = 0.0
        for slice_name in MOMENT_SLICES:
            mapper = builders["mappers"].get(slice_name)
            if mapper is None:
                continue
            t_map = time.perf_counter()
            payload = mapper(ctx)
            map_ms += (time.perf_counter() - t_map) * 1000
            payloads[slice_name] = payload
            t_write = time.perf_counter()
            await set_cached_slice(
                user_id, moment_id, slice_name, payload, moment_type=moment_type
            )
            write_ms += (time.perf_counter() - t_write) * 1000
        logger = __import__("logging").getLogger(__name__)
        logger.info(
            "BusinessProjectionRead momentId=%s momentType=%s slice=_bundle "
            "cacheSource=miss lockRole=builder redisReadMs=0.0 contextMs=%.1f "
            "mapMs=%.1f redisWriteMs=%.1f totalMs=%.1f",
            moment_id,
            moment_type,
            context_ms,
            map_ms,
            write_ms,
            context_ms + map_ms + write_ms,
        )
        return payloads

    @staticmethod
    async def _bundle_lock_slice(
        user_id: UUID, template: str
    ) -> str:
        """Frozen bundle key: user + moment(template) + projectionVersion.

        Lock slice name encodes the current pulse version so waiters on an old
        generation do not block a post-invalidate rebuild.
        """
        env = await projection_cache.get(user_id, template, "pulse")
        if env is None:
            env = await projection_cache.get_stale(user_id, template, "pulse")
        version = int(env.version) if env is not None else 0
        return f"_bundle:v{version}"

    async def _build_slice(
        self, user_id: UUID, moment_id: UUID, slice_type: str, moment_type: str
    ) -> dict:
        """Cold miss: single-flight under frozen ``_bundle`` lock; warm sibling slices.

        Pulse and Moments share this lock. Life/Memory must never use it.
        Failed builds release the lock and do not poison later requests.
        """
        import asyncio
        import time

        from app.domains.business.projection_cache import template_key

        template = template_key(moment_type, moment_id)
        bundle_lock = await self._bundle_lock_slice(user_id, template)

        async def _read() -> dict | None:
            existing = await projection_cache.get(user_id, template, slice_type)
            return existing.payload if existing is not None else None

        hit = await _read()
        if hit is not None:
            return hit

        acquired = await projection_cache.acquire_build_lock(
            user_id, template, bundle_lock
        )
        if not acquired:
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                hit = await _read()
                if hit is not None:
                    return hit
                await asyncio.sleep(0.05)
            # Re-resolve lock slice in case version moved during wait.
            bundle_lock = await self._bundle_lock_slice(user_id, template)
            acquired = await projection_cache.acquire_build_lock(
                user_id, template, bundle_lock
            )

        try:
            hit = await _read()
            if hit is not None:
                return hit
            payloads = await self._build_all_moment_slices(
                user_id, moment_id, moment_type
            )
            return payloads.get(slice_type) or {}
        finally:
            if acquired:
                await projection_cache.release_build_lock(
                    user_id, template, bundle_lock
                )

    async def get_pulse(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await require_moment_read_access(self.session, moment_id, user_id)
        mt = await self._moment_type(moment_id)
        return await cached_or_build(
            user_id, moment_id, "pulse",
            lambda: self._build_slice(user_id, moment_id, "pulse", mt),
            moment_type=mt,
            force_refresh=force_refresh,
        )

    async def get_moments(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await require_moment_read_access(self.session, moment_id, user_id)
        mt = await self._moment_type(moment_id)
        return await cached_or_build(
            user_id, moment_id, "moments",
            lambda: self._build_slice(user_id, moment_id, "moments", mt),
            moment_type=mt,
            force_refresh=force_refresh,
        )

    async def get_quick_add(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await require_moment_read_access(self.session, moment_id, user_id)
        mt = await self._moment_type(moment_id)
        return await cached_or_build(
            user_id, moment_id, "quick_add",
            lambda: self._build_slice(user_id, moment_id, "quick_add", mt),
            moment_type=mt,
            force_refresh=force_refresh,
        )

    async def get_vendor_ledger(
        self, user_id: UUID, moment_id: UUID, vendor_name: str
    ) -> dict:
        from app.domains.business.vendor_ledger import build_vendor_ledger

        await require_moment_read_access(self.session, moment_id, user_id)
        return await build_vendor_ledger(self.session, moment_id, vendor_name)

    async def get_action_catalog(self, user_id: UUID, moment_id: UUID) -> dict:
        """Always fresh catalog (small payload); also warms quick_add cache."""
        from app.domains.business.action_catalog import build_action_catalog_payload
        from app.domains.business.models import BusinessMomentMembers

        await require_moment_read_access(self.session, moment_id, user_id)
        mt = await self._moment_type(moment_id)
        result = await self.session.execute(
            select(
                BusinessMomentMembers.member_id,
                BusinessMomentMembers.name,
                BusinessMomentMembers.role,
                BusinessMomentMembers.user_id,
            ).where(
                BusinessMomentMembers.moment_id == moment_id,
                BusinessMomentMembers.member_status.in_(("active", "configured")),
            )
        )
        members = [
            {
                "member_id": str(row.member_id),
                "name": row.name,
                "role": row.role,
                "user_id": str(row.user_id) if row.user_id else None,
            }
            for row in result.all()
        ]
        from app.domains.business.vendor_suggestions import list_moment_vendors

        vendors = await list_moment_vendors(self.session, moment_id)
        payload = build_action_catalog_payload(
            moment_id=str(moment_id),
            moment_type=mt,
            members=members,
            vendors=vendors,
        )
        return payload

    async def get_renderer_metadata(
        self, user_id: UUID, moment_id: UUID, action_key: str
    ) -> dict:
        from fastapi import HTTPException, status

        from app.domains.business.action_catalog import build_renderer_metadata

        await require_moment_read_access(self.session, moment_id, user_id)
        mt = await self._moment_type(moment_id)
        meta = build_renderer_metadata(mt, action_key, moment_id=str(moment_id))
        if meta is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "invalid_action_for_template", "message": f"Unknown action: {action_key}"},
            )
        return meta

    # ---- Activity CRUD -------------------------------------------------- #
    async def create_activity(
        self,
        user_id: UUID,
        moment_id: UUID,
        action_type: str,
        title: str,
        *,
        subtitle: str | None = None,
        payload: dict[str, Any] | None = None,
        client_request_id: str | None = None,
        source: str = "quick_add",
        actor_name: str = "You",
    ) -> dict:
        return await self.activity.create(
            user_id, moment_id, action_type, title,
            subtitle=subtitle, payload=payload,
            client_request_id=client_request_id,
            source=source, actor_name=actor_name,
        )

    async def get_activity(self, user_id: UUID, moment_id: UUID, event_id: UUID) -> dict:
        return await self.activity.get(user_id, moment_id, event_id)

    async def list_activity(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        action: str | None = None,
        member_id: UUID | None = None,
        status_filter: str = "active",
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
        sort: str = "newest",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await self.activity.list(
            user_id,
            moment_id,
            action=action,
            member_id=member_id,
            status_filter=status_filter,
            date_from=date_from,
            date_to=date_to,
            search=search,
            sort=sort,
            page=page,
            page_size=page_size,
        )

    async def patch_activity(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: UUID,
        patch_data: dict[str, Any],
        *,
        actor_name: str = "You",
    ) -> dict:
        return await self.activity.patch(
            user_id, moment_id, event_id, patch_data, actor_name=actor_name
        )

    async def delete_activity(
        self, user_id: UUID, moment_id: UUID, event_id: UUID, *, actor_name: str = "You"
    ) -> dict:
        return await self.activity.delete_soft(
            user_id, moment_id, event_id, actor_name=actor_name
        )

    # ---- Cross-moment aggregates (Redis-first user agg) ----------------- #
    async def get_life(self, user_id: UUID, *, force_refresh: bool = False) -> dict:
        return await cached_or_build_user_agg(
            user_id,
            "life",
            lambda: build_life(self.session, user_id),
            force_refresh=force_refresh,
        )

    async def get_memory(self, user_id: UUID, *, force_refresh: bool = False) -> dict:
        return await cached_or_build_user_agg(
            user_id,
            "memory",
            lambda: build_memory(self.session, user_id),
            force_refresh=force_refresh,
        )
