"""Metadata API — public alias for the Reference Data Engine."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.domains.reference_data.service import get_reference_data_service

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/bootstrap")
async def get_metadata_bootstrap() -> dict:
    service = get_reference_data_service()
    payload = service.get_bootstrap().model_dump(mode="json")
    payload["metadata_version"] = payload.get("reference_data_version", service.get_version())
    return payload


@router.get("/options")
async def get_metadata_options(
    keys: str = Query(..., description="Comma-separated collection keys"),
) -> dict:
    service = get_reference_data_service()
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        return {
            "metadata_version": service.get_version(),
            "reference_data_version": service.get_version(),
            "data": {},
        }
    payload = service.get_options(key_list).model_dump(mode="json")
    payload["metadata_version"] = payload.get("reference_data_version", service.get_version())
    return payload
