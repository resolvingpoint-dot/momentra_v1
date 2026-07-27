"""Memory refresh task (per moment, per context).

context: ``personal`` | ``group`` | ``business``. Delegates to the matching
memory procedure; idempotent via snapshot upserts.
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.workers import procedures as procs
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="memory.refresh", bind=True, **RETRY_OPTS)
def refresh_memory(self, context: str, moment_id: str) -> dict:
    return run_async(_refresh(context, UUID(str(moment_id))))


async def _refresh(context: str, moment_id: UUID) -> dict:
    async with worker_session() as session:
        proc = await procs.refresh_memory(session, context, moment_id)
        await session.commit()
    logger.info("Refreshed %s memory for moment %s", context, moment_id)
    return {"context": context, "moment_id": str(moment_id), "procedure": proc, "status": "refreshed"}
