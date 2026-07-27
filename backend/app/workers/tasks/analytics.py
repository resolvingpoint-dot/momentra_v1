"""Analytics refresh task (per moment, per context).

context: ``personal`` | ``group`` | ``business``. Delegates to the matching
analytics / orchestration procedure; idempotent via snapshot upserts.
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.workers import procedures as procs
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="analytics.refresh", bind=True, **RETRY_OPTS)
def refresh_analytics(self, context: str, moment_id: str, user_id: str = "") -> dict:
    return run_async(
        _refresh(context, UUID(str(moment_id)), UUID(str(user_id)) if user_id else None)
    )


async def _refresh(context: str, moment_id: UUID, user_id: UUID | None) -> dict:
    async with worker_session() as session:
        proc = await procs.refresh_analytics(session, context, moment_id)
        if user_id is not None and context in {"group", "business"}:
            await procs.refresh_life360_snapshot(session, user_id)
        await session.commit()
    logger.info("Refreshed %s analytics for moment %s", context, moment_id)
    return {
        "context": context,
        "moment_id": str(moment_id),
        "procedure": proc,
        "status": "refreshed",
        "life360_refreshed": user_id is not None and context in {"group", "business"},
    }
