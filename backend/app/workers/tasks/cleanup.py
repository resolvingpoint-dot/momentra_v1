"""Cleanup task (celery beat, nightly).

Archives/expires stale rows and prunes old completed jobs via conditional
updates/deletes, which makes it fully idempotent: once a row no longer matches
its predicate a rerun affects zero rows.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.domains.business.repository import (
    BusinessMomentInvitationsRepository,
    BusinessNotificationsRepository,
    BusinessOrchestrationJobsRepository,
    BusinessQuickAddDraftsRepository,
)
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="cleanup.run", bind=True, **RETRY_OPTS)
def run_cleanup(self, job_retention_days: int = 30, draft_stale_days: int = 14) -> dict:
    return run_async(_cleanup(job_retention_days, draft_stale_days))


async def _cleanup(job_retention_days: int, draft_stale_days: int) -> dict:
    now = datetime.now(timezone.utc)
    job_cutoff = now - timedelta(days=job_retention_days)
    draft_cutoff = now - timedelta(days=draft_stale_days)

    async with worker_session() as session:
        notifications_repo = BusinessNotificationsRepository(session)
        invitations_repo = BusinessMomentInvitationsRepository(session)
        jobs_repo = BusinessOrchestrationJobsRepository(session)
        drafts_repo = BusinessQuickAddDraftsRepository(session)

        expired_notifications = await notifications_repo.update_where(
            {"expires_at__lt": now, "notification_status__notin": ["archived"]},
            {"notification_status": "archived"},
        )
        expired_invitations = await invitations_repo.update_where(
            {"expires_at__lt": now, "invite_status__in": ["pending", "sent"]},
            {"invite_status": "expired"},
        )
        stale_drafts = await drafts_repo.update_where(
            {"updated_at__lt": draft_cutoff, "draft_status": "active"},
            {"draft_status": "expired"},
        )
        deleted_jobs = await jobs_repo.delete_where(
            {"job_status": "completed", "completed_at__lt": job_cutoff},
        )
        await session.commit()

    summary = {
        "expired_notifications": expired_notifications,
        "expired_invitations": expired_invitations,
        "expired_drafts": stale_drafts,
        "deleted_jobs": deleted_jobs,
    }
    logger.info("Cleanup complete: %s", summary)
    return summary
