from __future__ import annotations

from app.core.errors import StateTransitionError

# Canonical lifecycle statuses used across contexts.
DRAFT = "DRAFT"
ACTIVE = "ACTIVE"
PAUSED = "PAUSED"
COMPLETED = "COMPLETED"
ARCHIVED = "ARCHIVED"
SETUP = "SETUP"

_TRANSITIONS: dict[str, set[str]] = {
    DRAFT: {ACTIVE, ARCHIVED},
    SETUP: {ACTIVE, DRAFT, ARCHIVED},
    ACTIVE: {PAUSED, COMPLETED, ARCHIVED},
    PAUSED: {ACTIVE, COMPLETED, ARCHIVED},
    COMPLETED: {ARCHIVED},
    ARCHIVED: set(),
}


def assert_transition(from_status: str, to_status: str, *, label: str = "moment") -> None:
    allowed = _TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        if from_status == to_status:
            raise StateTransitionError(f"{label} is already {to_status}")
        raise StateTransitionError(
            f"Cannot transition {label} from {from_status} to {to_status}"
        )


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in _TRANSITIONS.get(from_status, set())
