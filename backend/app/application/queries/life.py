"""Life Timeline / command-center reads for GraphQL."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal


class LifeScope(str, Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@dataclass
class LifeDTO:
    scope: LifeScope
    is_empty: bool
    active_moment_count: int
    date_range_label: str | None = None
    metrics: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def _from_dict(scope: LifeScope, data: dict[str, Any]) -> LifeDTO:
    metrics = data.get("metrics")
    if metrics is not None and not isinstance(metrics, dict):
        try:
            metrics = dict(metrics) if hasattr(metrics, "items") else {"value": metrics}
        except Exception:  # noqa: BLE001
            metrics = {"value": str(metrics)}
    return LifeDTO(
        scope=scope,
        is_empty=bool(data.get("is_empty", True)),
        active_moment_count=int(data.get("active_moment_count") or 0),
        date_range_label=data.get("date_range_label"),
        metrics=metrics if isinstance(metrics, dict) else None,
        payload=data,
    )


async def get_life(
    session: AsyncSession,
    principal: Principal,
    scope: LifeScope | str,
    *,
    force_refresh: bool = False,
) -> LifeDTO:
    """Return Life command-center for PERSONAL / GROUP / BUSINESS (AuthN only)."""
    scope_val = LifeScope(scope) if not isinstance(scope, LifeScope) else scope
    user_id = principal.user_id

    if scope_val is LifeScope.PERSONAL:
        from app.domains.personal.app_service import PersonalAppService

        data = await PersonalAppService(session).life(
            user_id, force_refresh=force_refresh
        )
        return _from_dict(scope_val, data if isinstance(data, dict) else {})

    if scope_val is LifeScope.GROUP:
        from app.domains.group.app_service import GroupAppService

        data = await GroupAppService(session).life(user_id)
        return _from_dict(scope_val, data if isinstance(data, dict) else {})

    if scope_val is LifeScope.BUSINESS:
        from app.domains.business.active_service import BusinessActiveService

        data = await BusinessActiveService(session).get_life(
            user_id, force_refresh=force_refresh
        )
        return _from_dict(scope_val, data if isinstance(data, dict) else {})

    raise ValueError(f"Unsupported life scope: {scope_val}")
