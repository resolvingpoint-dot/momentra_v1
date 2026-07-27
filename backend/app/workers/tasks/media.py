"""Media processing task.

Processes an uploaded ``business_attachment_files`` row (e.g. thumbnailing /
transcoding / virus scan -- stubbed here as deterministic metadata derivation).
Idempotent via a Redis marker written only after success, so duplicate
submissions are skipped while failed attempts still retry.
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.domains.business.models import BusinessAttachmentFiles
from app.domains.business.repository import BusinessAttachmentFilesRepository
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session
from app.workers.idempotency import is_done, mark_done

logger = logging.getLogger(__name__)


def _derive_metadata(f: BusinessAttachmentFiles) -> dict:
    """Deterministic 'processing' output. Replace with real derivative generation."""
    return {
        "file_type": f.file_type,
        "size_bytes": f.file_size_bytes,
        "storage_path": f.storage_path,
        "is_image": (f.file_type or "").lower().startswith("image/"),
    }


@celery_app.task(name="media.process", bind=True, **RETRY_OPTS)
def process_media(self, file_id: str) -> dict:
    return run_async(_process(UUID(str(file_id))))


async def _process(file_id: UUID) -> dict:
    marker = f"media:{file_id}"
    if is_done(marker):
        return {"file_id": str(file_id), "status": "already_processed"}

    async with worker_session() as session:
        repo = BusinessAttachmentFilesRepository(session)
        attachment = await repo.get_by_id(file_id)
        if attachment is None:
            return {"file_id": str(file_id), "status": "not_found"}
        result = _derive_metadata(attachment)
        logger.info("Processed media %s (%s)", file_id, result["file_type"])

    mark_done(marker)
    return {"file_id": str(file_id), "status": "processed", "metadata": result}
