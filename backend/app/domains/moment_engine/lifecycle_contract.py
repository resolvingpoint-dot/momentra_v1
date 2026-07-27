"""Cross-context moment lifecycle contract helpers.

Used by Personal / Group / Business services so clients get a stable typed
response, replacement selection, and diagnosable access denials — without a
second lifecycle engine.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Iterable
from uuid import UUID

from app.core.errors import PermissionDeniedError, StateTransitionError
from app.domains.moment_engine.state import ACTIVE, ARCHIVED, COMPLETED, DRAFT, PAUSED, SETUP
from app.domains.moments.models import MomentModel

logger = logging.getLogger(__name__)

# Canonical error code for illegal transitions (HTTP 409).
LIFECYCLE_TRANSITION_INVALID = "lifecycle_transition_invalid"

# Prefer ACTIVE, then viewable paused/completed, then drafts — never ARCHIVED.
_REPLACEMENT_RANK = {
    ACTIVE: 0,
    PAUSED: 1,
    COMPLETED: 2,
    DRAFT: 3,
    SETUP: 3,
}


def hash_user_id(user_id: UUID | str) -> str:
    raw = str(user_id).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def log_access_denied(
    *,
    context_type: str,
    moment_id: UUID | str | None,
    moment_type: str | None,
    user_id: UUID | str,
    action: str,
    denial_reason: str,
    owner_match: bool | None = None,
    membership_found: bool | None = None,
    membership_status: str | None = None,
    role: str | None = None,
    required_capability: str | None = None,
) -> None:
    logger.info(
        "event=MomentAccessDenied contextType=%s momentId=%s momentType=%s "
        "userHash=%s action=%s ownerMatch=%s membershipFound=%s "
        "membershipStatus=%s role=%s requiredCapability=%s denialReason=%s",
        context_type,
        moment_id,
        moment_type,
        hash_user_id(user_id),
        action,
        owner_match,
        membership_found,
        membership_status,
        role,
        required_capability,
        denial_reason,
    )


def deny_access(
    *,
    context_type: str,
    moment_id: UUID | str | None,
    moment_type: str | None,
    user_id: UUID | str,
    action: str,
    denial_reason: str,
    message: str,
    owner_match: bool | None = None,
    membership_found: bool | None = None,
    membership_status: str | None = None,
    role: str | None = None,
    required_capability: str | None = None,
) -> PermissionDeniedError:
    log_access_denied(
        context_type=context_type,
        moment_id=moment_id,
        moment_type=moment_type,
        user_id=user_id,
        action=action,
        denial_reason=denial_reason,
        owner_match=owner_match,
        membership_found=membership_found,
        membership_status=membership_status,
        role=role,
        required_capability=required_capability,
    )
    return PermissionDeniedError(
        message,
        code=denial_reason,
        details={
            "denial_reason": denial_reason,
            "context_type": context_type,
            "moment_id": str(moment_id) if moment_id else None,
            "action": action,
        },
    )


def raise_invalid_transition(message: str, *, details: dict[str, Any] | None = None) -> None:
    raise StateTransitionError(
        message,
        code=LIFECYCLE_TRANSITION_INVALID,
        details=details,
    )


def _norm(value: str | None) -> str:
    return (value or "").strip().upper()


def is_selectable(status: str | None) -> bool:
    return _norm(status) != ARCHIVED and bool(_norm(status))


def pick_replacement_moment(
    inventory: Iterable[MomentModel],
    *,
    exclude_id: UUID | None = None,
    preferred_id: UUID | None = None,
) -> tuple[str | None, str | None]:
    """Return (moment_id, moment_type_code) using sprint selection rules."""
    candidates: list[MomentModel] = []
    for m in inventory:
        if exclude_id is not None and m.id == exclude_id:
            continue
        if not is_selectable(m.status):
            continue
        # Wrong-context filtering is the caller's responsibility.
        candidates.append(m)

    if preferred_id is not None:
        for m in candidates:
            if m.id == preferred_id:
                return str(m.id), m.moment_type

    def sort_key(m: MomentModel) -> tuple[int, float]:
        rank = _REPLACEMENT_RANK.get(_norm(m.status), 99)
        # Prefer newer updated_at within the same rank.
        ts = m.updated_at.timestamp() if m.updated_at else 0.0
        return (rank, -ts)

    if not candidates:
        return None, None
    best = sorted(candidates, key=sort_key)[0]
    return str(best.id), best.moment_type


def build_lifecycle_response(
    *,
    moment: MomentModel,
    context_type: str,
    previous_status: str,
    module_state: str | None = None,
    replacement_moment_id: str | None = None,
    replacement_moment_type_code: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Typed lifecycle payload — optional fields stay backward compatible."""
    updated = None
    if moment.updated_at is not None:
        updated = moment.updated_at.isoformat()
    payload: dict[str, Any] = {
        "moment_id": str(moment.id),
        "context_type": context_type,
        "moment_type_code": moment.moment_type or "",
        "previous_status": previous_status,
        "status": moment.status,
        "updated_at": updated,
        "module_state": module_state,
        "replacement_moment_id": replacement_moment_id,
        "replacement_moment_type_code": replacement_moment_type_code,
        # Legacy aliases used by existing clients
        "lifecycle_status": moment.status,
        "orchestration_state": moment.setup_state,
        "moment_name": moment.title,
        "is_archived": _norm(moment.status) == ARCHIVED,
    }
    if extra:
        payload.update(extra)
    return payload


def log_lifecycle_transition(
    *,
    context_type: str,
    moment_id: UUID | str,
    moment_type: str | None,
    action: str,
    previous_status: str,
    final_status: str,
    permission_result: str = "allowed",
    module_state: str | None = None,
    replacement_moment_id: str | None = None,
    transaction_ms: int | None = None,
    bootstrap_invalidate_ms: int | None = None,
    projection_invalidate_ms: int | None = None,
    total_ms: int | None = None,
) -> None:
    logger.info(
        "event=MomentLifecycleTransition contextType=%s momentId=%s momentType=%s "
        "action=%s previousStatus=%s finalStatus=%s permissionResult=%s "
        "moduleState=%s replacementMomentId=%s transactionMs=%s "
        "bootstrapInvalidateMs=%s projectionInvalidateMs=%s totalMs=%s",
        context_type,
        moment_id,
        moment_type,
        action,
        previous_status,
        final_status,
        permission_result,
        module_state,
        replacement_moment_id,
        transaction_ms,
        bootstrap_invalidate_ms,
        projection_invalidate_ms,
        total_ms,
    )
