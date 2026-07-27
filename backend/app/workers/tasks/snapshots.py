"""Snapshot refresh task.

Delegates to the user-scoped snapshot procedures (life360 / circle / personal
life snapshot). Idempotent: the procedures upsert their snapshot rows.
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.core import cache as core_cache
from app.domains.personal.projection.warm import warm_projection_cache
from app.workers import procedures as procs
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="snapshots.refresh", bind=True, **RETRY_OPTS)
def refresh_snapshots(self, user_id: str) -> dict:
    return run_async(_refresh(UUID(str(user_id))))


async def _refresh(user_id: UUID) -> dict:
    lock_key = f"snapshot_refresh:{user_id}"
    acquired = await core_cache.acquire_lock(lock_key, ttl=120)
    if not acquired:
        logger.info("Skipped duplicate snapshot refresh for user %s", user_id)
        return {"user_id": str(user_id), "status": "skipped", "reason": "deduped"}

    try:
        async with worker_session() as session:
            procedures = await procs.refresh_user_snapshots(session, user_id)
            await session.commit()
            try:
                await warm_projection_cache(session, user_id)
            except Exception:
                logger.warning(
                    "Projection warm failed for user %s", user_id, exc_info=True
                )
        logger.info("Refreshed snapshots for user %s", user_id)
        return {"user_id": str(user_id), "procedures": procedures, "status": "refreshed"}
    finally:
        await core_cache.release_lock(lock_key)
