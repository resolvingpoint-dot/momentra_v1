"""Dev/stub object storage endpoints for signed PUT URLs.

When ``STORAGE_PUBLIC_BASE_URL`` is unset, ``build_upload_url`` returns
``/local-uploads/{path}``. Clients must PUT the bytes here (against the API
origin), then call the normal confirm endpoint.
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response, status

logger = logging.getLogger(__name__)

router = APIRouter(tags=["local-uploads"])

_ROOT = Path(__file__).resolve().parents[2] / ".local-uploads"


def _safe_path(relative: str) -> Path:
    cleaned = (relative or "").replace("\\", "/").lstrip("/")
    if not cleaned or ".." in cleaned.split("/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path")
    target = (_ROOT / cleaned).resolve()
    root = _ROOT.resolve()
    if target != root and root not in target.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path")
    return target


@router.put("/local-uploads/{object_path:path}", status_code=status.HTTP_200_OK)
async def put_local_upload(object_path: str, request: Request) -> dict[str, str]:
    data = await request.body()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty body")
    target = _safe_path(object_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    content_type = request.headers.get("content-type") or "application/octet-stream"
    logger.info("Local upload stored %s (%d bytes, %s)", object_path, len(data), content_type)
    return {"storage_path": object_path, "bytes": str(len(data))}


@router.get("/local-uploads/{object_path:path}")
async def get_local_upload(object_path: str) -> Response:
    target = _safe_path(object_path)
    if not target.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    suffix = target.suffix.lower()
    media = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
        ".pdf": "application/pdf",
    }.get(suffix, "application/octet-stream")
    return Response(content=target.read_bytes(), media_type=media)
