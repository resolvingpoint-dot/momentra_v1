"""Orchestration job processing.

``process_job`` runs the generic ``sp_process_orchestration_job`` for a single
business orchestration job. ``scan_jobs`` (celery beat, every minute) finds
queued jobs and fans out one ``process_job`` per row.

Idempotent: the procedure flips the job to ``processing``/``completed`` and only
re-runs idempotent snapshot refreshes; ``scan_jobs`` selects only ``queued`` rows
so completed jobs are never re-dispatched. Fan-out happens *outside* the event
loop so eager-mode execution does not nest ``asyncio.run``.
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.domains.business.repository import BusinessOrchestrationJobsRepository
from app.workers import procedures as procs
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="orchestration.process_job", bind=True, **RETRY_OPTS)
def process_orchestration_job(self, job_id: str) -> dict:
    return run_async(_process(UUID(str(job_id))))


async def _process(job_id: UUID) -> dict:
    async with worker_session() as session:
        await procs.process_orchestration_job(session, job_id)
        await session.commit()
    logger.info("Processed orchestration job %s", job_id)
    return {"job_id": str(job_id), "status": "processed"}


@celery_app.task(name="orchestration.scan_jobs", bind=True, **RETRY_OPTS)
def scan_orchestration_jobs(self, limit: int = 100) -> dict:
    job_ids = run_async(_queued_job_ids(limit))
    for job_id in job_ids:
        process_orchestration_job.delay(job_id)
    logger.info("Dispatched %d queued orchestration jobs", len(job_ids))
    return {"dispatched": len(job_ids)}


async def _queued_job_ids(limit: int) -> list[str]:
    async with worker_session() as session:
        repo = BusinessOrchestrationJobsRepository(session)
        jobs = await repo.list(filters={"job_status": "queued"}, order_by="queued_at", limit=limit)
        return [str(j.job_id) for j in jobs]
