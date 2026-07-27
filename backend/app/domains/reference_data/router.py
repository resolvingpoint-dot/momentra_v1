from __future__ import annotations

from fastapi import APIRouter, Query

from app.domains.reference_data.service import get_reference_data_service

router = APIRouter(prefix="/reference-data", tags=["reference-data"])


@router.get("/bootstrap")
async def get_reference_data_bootstrap() -> dict:
    service = get_reference_data_service()
    return service.get_bootstrap().model_dump(mode="json")


@router.get("/options")
async def get_reference_data_options(
    keys: str = Query(..., description="Comma-separated collection keys"),
) -> dict:
    service = get_reference_data_service()
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        return {"reference_data_version": service.get_version(), "data": {}}
    return service.get_options(key_list).model_dump(mode="json")
