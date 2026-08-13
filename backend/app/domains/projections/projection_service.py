"""Cache-first projection read path with single-flight protection."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import (
    set_build_coalesced,
    set_cache_hit,
    set_projection_build_ms,
    set_projection_lock,
    set_projection_state,
    set_projection_version,
    set_refresh_enqueued,
)
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.templates.registry import get_template_projection_registry
from app.domains.projections import projection_cache
from app.domains.projections.projection_builder import (
    ProjectionSliceBuilder,
    compose_aggregate_pulse,
    extract_aggregate_pulse_block,
)
from app.domains.projections.projection_keys import PERSONAL_LIFE_TEMPLATE
from app.domains.projections.projection_metrics import record_cache_hit, record_cache_miss

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 0.05
_POLL_TIMEOUT = 2.0


class ProjectionReadService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._builder = ProjectionSliceBuilder(session)

    async def get_slice(
        self,
        user_id: UUID,
        template: str,
        slice_type: str,
        *,
        force_refresh: bool = False,
        reason: str | None = None,
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(template)
        if slice_type == "life" and code == PERSONAL_LIFE_TEMPLATE:
            cache_template = PERSONAL_LIFE_TEMPLATE
        else:
            cache_template = code

        # force_refresh must never destroy the last usable payload.
        # FRESH → STALE → enqueue; serve stale. Sync build only on true miss.
        if force_refresh:
            logger.warning(
                "force_refresh on personal GET template=%s slice=%s — SWR, not sync rebuild",
                cache_template,
                slice_type,
            )
            await projection_cache.mark_stale(user_id, cache_template, slice_type)
            enqueued = self._enqueue_stale_rebuild(
                user_id, cache_template, slice_type, reason="manual"
            )
            set_refresh_enqueued(enqueued, reason="manual")
            envelope = await projection_cache.get(user_id, cache_template, slice_type)
            if envelope is not None:
                record_cache_hit()
                set_cache_hit(True)
                set_build_coalesced(True)
                set_projection_state("stale")
                set_projection_lock("none")
                set_projection_version(envelope.version)
                return envelope.payload
            # True miss after mark_stale — fall through to sync build.

        envelope = await projection_cache.get(user_id, cache_template, slice_type)
        if envelope is not None and not envelope.stale:
            record_cache_hit()
            set_cache_hit(True)
            set_projection_state("fresh")
            set_projection_lock("none")
            set_refresh_enqueued(False)
            set_projection_version(envelope.version)
            return envelope.payload

        if envelope is not None and envelope.stale:
            record_cache_hit()
            set_cache_hit(True)
            set_build_coalesced(True)
            set_projection_state("stale")
            set_projection_lock("none")
            set_projection_version(envelope.version)
            enqueued = self._enqueue_stale_rebuild(
                user_id, cache_template, slice_type, reason="stale_serve"
            )
            set_refresh_enqueued(enqueued, reason="stale_serve")
            return envelope.payload

        record_cache_miss()
        set_projection_state("miss")
        return await self._get_or_build(
            user_id, cache_template, slice_type, reason=reason or "cold_miss"
        )

    @staticmethod
    def _enqueue_stale_rebuild(
        user_id: UUID,
        template: str,
        slice_type: str,
        *,
        reason: str = "stale_serve",
    ) -> bool:
        """Serve-stale path: refresh active key via Celery (safe vs request session)."""
        try:
            from app.workers.tasks import projections as proj_tasks

            task_by_slice = {
                "pulse": proj_tasks.refresh_pulse_projection,
                "moments": proj_tasks.refresh_moments_projection,
                "memory": proj_tasks.refresh_memory_projection,
                "life": proj_tasks.refresh_life_projection,
            }
            task = task_by_slice.get(slice_type)
            if task is None:
                return False
            task.delay(str(user_id), template, reason)
            return True
        except Exception:  # noqa: BLE001
            logger.debug(
                "Failed to enqueue stale rebuild user=%s template=%s slice=%s",
                user_id,
                template,
                slice_type,
                exc_info=True,
            )
            return False

    async def _get_or_build(
        self,
        user_id: UUID,
        template: str,
        slice_type: str,
        *,
        reason: str | None = None,
    ) -> dict[str, Any]:
        stale = await projection_cache.get_stale(user_id, template, slice_type)
        acquired = await projection_cache.acquire_build_lock(user_id, template, slice_type)
        if not acquired:
            set_projection_lock("contended")
            if stale is not None:
                set_build_coalesced(True)
                set_cache_hit(True)
                set_projection_state("stale")
                set_projection_version(stale.version)
                enqueued = self._enqueue_stale_rebuild(
                    user_id, template, slice_type, reason="stale_serve"
                )
                set_refresh_enqueued(enqueued, reason="stale_serve")
                return stale.payload
            waited = await self._wait_for_slice(user_id, template, slice_type)
            if waited is not None:
                set_build_coalesced(True)
                set_cache_hit(True)
                set_projection_state("fresh" if not waited.stale else "stale")
                set_projection_version(waited.version)
                set_refresh_enqueued(False)
                return waited.payload
            acquired = await projection_cache.acquire_build_lock(user_id, template, slice_type)

        try:
            if acquired:
                set_projection_lock("acquired")
                start = time.perf_counter()
                payload = await self._build_and_store(
                    user_id, template, slice_type, reason=reason or "cold_miss"
                )
                set_projection_build_ms((time.perf_counter() - start) * 1000)
                set_cache_hit(False)
                set_projection_state("miss")
                set_refresh_enqueued(False, reason="cold_miss")
                return payload
            set_projection_lock("contended")
            if stale is not None:
                set_build_coalesced(True)
                set_cache_hit(True)
                set_projection_state("stale")
                set_projection_version(stale.version)
                return stale.payload
            set_projection_lock("acquired")
            payload = await self._build_and_store(
                user_id, template, slice_type, reason=reason or "cold_miss"
            )
            set_projection_state("miss")
            set_refresh_enqueued(False, reason="cold_miss")
            return payload
        finally:
            if acquired:
                await projection_cache.release_build_lock(user_id, template, slice_type)

    async def _wait_for_slice(
        self, user_id: UUID, template: str, slice_type: str
    ) -> projection_cache.ProjectionEnvelope | None:
        deadline = time.monotonic() + _POLL_TIMEOUT
        while time.monotonic() < deadline:
            envelope = await projection_cache.get(user_id, template, slice_type)
            if envelope is not None:
                return envelope
            await asyncio.sleep(_POLL_INTERVAL)
        return await projection_cache.get_stale(user_id, template, slice_type)

    async def _build_and_store(
        self,
        user_id: UUID,
        template: str,
        slice_type: str,
        *,
        reason: str | None = None,
    ) -> dict[str, Any]:
        if slice_type == "pulse":
            return await self._builder.build_pulse(user_id, template, reason=reason)
        if slice_type == "moments":
            return await self._builder.build_moments(user_id, template, reason=reason)
        if slice_type == "memory":
            return await self._builder.build_memory(user_id, template, reason=reason)
        if slice_type == "life":
            if template == PERSONAL_LIFE_TEMPLATE:
                return await self._builder.build_personal_life(
                    user_id, reason=reason, force_refresh=False
                )
            return await self._builder.build_template_life(user_id, template, reason=reason)
        raise ValueError(f"Unknown projection slice: {slice_type}")

    async def get_aggregate_pulse(
        self,
        user_id: UUID,
        active_templates: list[str],
        *,
        active_count: int,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        registry = get_template_projection_registry()
        codes = [
            code
            for code in active_templates
            if registry.is_registered(code) and hasattr(registry.resolve(code), "pulse")
        ]

        async def _one(code: str) -> tuple[str, dict[str, Any] | None]:
            try:
                slice_payload = await self.get_slice(
                    user_id, code, "pulse", force_refresh=force_refresh
                )
                return code, extract_aggregate_pulse_block(code, slice_payload)
            except Exception:
                logger.exception("Failed to read pulse slice for %s", code)
                return code, None

        results = await asyncio.gather(*(_one(code) for code in codes))
        blocks: dict[str, dict[str, Any] | None] = {code: block for code, block in results}
        return compose_aggregate_pulse(blocks, active_count=active_count)

    async def get_personal_life(
        self, user_id: UUID, *, force_refresh: bool = False
    ) -> dict[str, Any]:
        return await self.get_slice(
            user_id,
            PERSONAL_LIFE_TEMPLATE,
            "life",
            force_refresh=force_refresh,
        )
