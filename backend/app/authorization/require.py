"""Central ``require(principal, action, resource)`` dispatching to domain gates."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal
from app.authorization.cache import get_cached_decision, set_cached_decision
from app.core.errors import NotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)

# Starter action vocabulary (see docs/adr/0003-central-authz.md).
GROUP_MOMENT_VIEW = "group.moment.view"
GROUP_EXPENSE_CREATE = "group.expense.create"
BUSINESS_MOMENT_VIEW = "business.moment.view"
BUSINESS_WORKSPACE_VIEW = "business.workspace.view"
BUSINESS_FINANCE_VIEW = "business.finance.view"
PERSONAL_MOMENT_OWN = "personal.moment.own"


@dataclass(frozen=True, slots=True)
class ResourceRef:
    kind: str  # group_moment | business_moment | business_workspace | personal_moment
    id: UUID


def _principal_user_id(principal: Principal | UUID) -> UUID:
    if isinstance(principal, UUID):
        return principal
    return principal.user_id


def _map_http_exception(exc: HTTPException) -> None:
    """Re-raise domain HTTPException as AppError for stable envelopes."""
    detail = exc.detail
    message = detail if isinstance(detail, str) else str(detail)
    code = "permission_denied"
    if isinstance(detail, dict) and detail.get("code"):
        code = str(detail["code"])
        message = str(detail.get("message") or message)
    if exc.status_code == 404:
        raise NotFoundError(message, code="not_found") from exc
    if exc.status_code == 403:
        raise PermissionDeniedError(message, code=code) from exc
    raise PermissionDeniedError(message, code=code, status_code=exc.status_code) from exc


async def require(
    session: AsyncSession,
    principal: Principal | UUID,
    action: str,
    resource: ResourceRef,
    *,
    use_cache: bool = True,
) -> Any:
    """Enforce ``action`` on ``resource`` for the given principal.

    Delegates to existing domain access helpers — does not invent parallel rules.
    Returns domain helper results when available (e.g. MomentModel, membership).

    Workers may pass a bare ``UUID`` actor id instead of a full Principal.
    """
    user_id = _principal_user_id(principal)
    cache_key_parts = (str(user_id), resource.kind, str(resource.id), action)

    if use_cache:
        cached = await get_cached_decision(*cache_key_parts)
        # Only short-circuit cached denials. Allowed decisions still re-check so
        # callers receive live domain objects and membership removals apply ≤TTL.
        if cached is False:
            raise PermissionDeniedError(
                "Permission denied",
                code="permission_denied",
            )

    try:
        result = await _dispatch(session, user_id, action, resource)
    except HTTPException as exc:
        if use_cache and exc.status_code in (403, 404):
            await set_cached_decision(*cache_key_parts, allowed=False)
        _map_http_exception(exc)
        raise  # unreachable; keeps type-checkers happy
    except (NotFoundError, PermissionDeniedError):
        if use_cache:
            await set_cached_decision(*cache_key_parts, allowed=False)
        raise

    if use_cache:
        await set_cached_decision(*cache_key_parts, allowed=True)
    return result


async def _dispatch(
    session: AsyncSession,
    user_id: UUID,
    action: str,
    resource: ResourceRef,
) -> Any:
    if resource.kind == "group_moment" and action in (
        GROUP_MOMENT_VIEW,
        GROUP_EXPENSE_CREATE,
    ):
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(session, user_id, resource.id)

    if resource.kind == "business_moment" and action == BUSINESS_MOMENT_VIEW:
        from app.domains.business.permissions import require_moment_read_access

        await require_moment_read_access(session, resource.id, user_id)
        return None

    if resource.kind == "business_workspace" and action == BUSINESS_WORKSPACE_VIEW:
        from app.domains.business.permissions import require_workspace_member

        return await require_workspace_member(session, resource.id, user_id)

    if resource.kind == "business_moment" and action == BUSINESS_FINANCE_VIEW:
        from app.domains.business.permissions import (
            BusinessPermissionError,
            get_active_member,
            is_privileged_member,
            require_moment_read_access,
        )

        await require_moment_read_access(session, resource.id, user_id)
        member = await get_active_member(session, resource.id, user_id)
        if member is not None and is_privileged_member(member):
            return member
        if member is None:
            return None
        raise BusinessPermissionError(
            "business_permission_denied",
            "Member lacks finance permission.",
        )

    if resource.kind == "personal_moment" and action == PERSONAL_MOMENT_OWN:
        from app.domains.moments.repository import MomentRepository

        moment = await MomentRepository(session).get_by_user_and_id(user_id, resource.id)
        if moment is None:
            raise NotFoundError("Moment not found", code="not_found")
        return moment

    raise PermissionDeniedError(
        f"Unknown action/resource: {action} on {resource.kind}",
        code="unknown_authz_action",
    )
