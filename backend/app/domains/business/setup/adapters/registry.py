"""Registry of Business setup adapters."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.catalog import (
    BUSINESS_OPERATIONS,
    BUSINESS_RUNWAY,
    TEAM_OPERATIONS,
    normalize_moment_type_code,
)
from app.domains.business.setup.adapters.business_operations import BusinessOperationsAdapter
from app.domains.business.setup.adapters.business_runway import BusinessRunwayAdapter
from app.domains.business.setup.adapters.team_operations import TeamOperationsAdapter

_FACTORIES = {
    TEAM_OPERATIONS: TeamOperationsAdapter,
    BUSINESS_RUNWAY: BusinessRunwayAdapter,
    BUSINESS_OPERATIONS: BusinessOperationsAdapter,
}


def get_adapter(moment_type_code: str, session: AsyncSession | None = None):
    canonical = normalize_moment_type_code(moment_type_code)
    if canonical is None or canonical not in _FACTORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No setup adapter for moment type: {moment_type_code}",
        )
    adapter = _FACTORIES[canonical](session)
    if session is not None:
        adapter.bind(session)
    return adapter
