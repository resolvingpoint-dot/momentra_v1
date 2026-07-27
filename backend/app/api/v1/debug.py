"""Development-only debug endpoints (gated by settings.debug)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.version_registry import get_platform_versions
from app.dependencies.auth import get_current_user_id
from app.domains.moment_engine.registry import get_domain_registry
from app.domains.moment_engine.templates import get_template_registry
from app.domains.personal.catalog import MOMENT_TYPES
from app.domains.personal.life_operations.quick_add.handlers.registry import (
    list_registered_handlers,
)
from app.domains.personal.models import PersonalRuntimeSnapshots
from app.shared.events.models import DomainEventLog

router = APIRouter(prefix="/debug", tags=["debug"])


def _require_debug() -> None:
    if not settings.debug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.get("/snapshot-health")
async def snapshot_health(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    _require_debug()
    result = await db.execute(
        select(PersonalRuntimeSnapshots)
        .where(PersonalRuntimeSnapshots.user_id == user_id)
        .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
    )
    rows = list(result.scalars().all())
    by_type: dict[str, dict[str, Any]] = {}
    for row in rows:
        code = row.moment_type_code
        if code in by_type:
            continue
        by_type[code] = {
            "moment_id": str(row.moment_id),
            "snapshot_date": row.snapshot_date.isoformat(),
            "runtime_state_label": row.runtime_state_label,
            "primary_score": float(row.primary_score),
            "trend_direction": row.trend_direction,
        }
    count_result = await db.execute(
        select(func.count())
        .select_from(PersonalRuntimeSnapshots)
        .where(PersonalRuntimeSnapshots.user_id == user_id)
    )
    total = int(count_result.scalar_one() or 0)
    return {
        "user_id": str(user_id),
        "total_snapshots": total,
        "latest_by_moment_type": by_type,
        "healthy": total > 0,
    }


@router.get("/events")
async def domain_events(
    moment_id: UUID = Query(...),
    limit: int = Query(50, ge=1, le=200),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    _require_debug()
    result = await db.execute(
        select(DomainEventLog)
        .where(
            DomainEventLog.moment_id == moment_id,
            DomainEventLog.user_id == user_id,
        )
        .order_by(DomainEventLog.created_at.desc())
        .limit(limit)
    )
    events = [
        {
            "event_id": str(row.event_id),
            "name": row.name,
            "user_id": str(row.user_id),
            "moment_id": str(row.moment_id),
            "context": row.context,
            "moment_type": row.moment_type,
            "payload": row.payload,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in result.scalars().all()
    ]
    return {"moment_id": str(moment_id), "events": events, "count": len(events)}


@router.get("/projection-metrics")
async def projection_metrics(
    user_id: UUID = Depends(get_current_user_id),
) -> dict[str, Any]:
    _require_debug()
    from app.domains.personal.catalog import MOMENT_TYPES
    from app.domains.projections import projection_cache
    from app.domains.projections.projection_keys import PERSONAL_LIFE_TEMPLATE
    from app.domains.projections.projection_metrics import get_counters, get_last_builder_stage

    slices: list[dict[str, Any]] = []
    for mt in MOMENT_TYPES:
        for slice_type in ("pulse", "moments", "memory", "life"):
            env = await projection_cache.get(user_id, mt.code, slice_type)
            slices.append(
                {
                    "template": mt.code,
                    "slice": slice_type,
                    "exists": env is not None,
                    "version": env.version if env else None,
                    "updated_at": env.updated_at if env else None,
                    "stale": env.stale if env else False,
                    "ttl_seconds": await projection_cache.ttl(user_id, mt.code, slice_type),
                }
            )
    personal_life = await projection_cache.get(user_id, PERSONAL_LIFE_TEMPLATE, "life")
    slices.append(
        {
            "template": PERSONAL_LIFE_TEMPLATE,
            "slice": "life",
            "exists": personal_life is not None,
            "version": personal_life.version if personal_life else None,
            "updated_at": personal_life.updated_at if personal_life else None,
            "stale": personal_life.stale if personal_life else False,
            "ttl_seconds": await projection_cache.ttl(
                user_id, PERSONAL_LIFE_TEMPLATE, "life"
            ),
        }
    )
    return {
        "user_id": str(user_id),
        "counters": get_counters(),
        "last_builder_stage": get_last_builder_stage(),
        "slices": slices,
    }


@router.get("/registry")
async def registry_introspection(
    _user_id: UUID = Depends(get_current_user_id),
) -> dict[str, Any]:
    _require_debug()
    template_reg = get_template_registry()
    templates = [
        {
            "context": t.context,
            "moment_type": t.moment_type,
            "initial_status": t.initial_status,
            "worker_context": t.worker_context,
            "refresh_on_create": t.refresh_on_create,
        }
        for t in template_reg._templates.values()
    ]
    domain_reg = get_domain_registry()
    domains = [
        {
            "context": reg.context,
            "moment_type": reg.template.moment_type,
            "service": reg.service.__name__ if reg.service else None,
        }
        for reg in domain_reg._domains.values()
    ]
    quick_add = list_registered_handlers()
    setup = [
        {
            "moment_type_code": mt.code,
            "moment_type_name": mt.name,
            "field_keys": ["moment_name", "focus"],
        }
        for mt in MOMENT_TYPES
    ]
    versions = get_platform_versions().as_dict()
    return {
        "templates": templates,
        "domains": domains,
        "quick_add_handlers": quick_add,
        "setup_moment_types": setup,
        "versions": versions,
    }
