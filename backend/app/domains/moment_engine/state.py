from __future__ import annotations

from app.core.errors import StateTransitionError

# Canonical lifecycle statuses used across contexts.
DRAFT = "DRAFT"
ACTIVE = "ACTIVE"
PAUSED = "PAUSED"
COMPLETED = "COMPLETED"
ARCHIVED = "ARCHIVED"
DELETED = "DELETED"
SETUP = "SETUP"

# DELETED is a terminal purge tombstone (ops data cleared, analytics retained).
_TRANSITIONS: dict[str, set[str]] = {
    DRAFT: {ACTIVE, ARCHIVED, DELETED},
    SETUP: {ACTIVE, DRAFT, ARCHIVED, DELETED},
    ACTIVE: {PAUSED, COMPLETED, ARCHIVED, DELETED},
    PAUSED: {ACTIVE, COMPLETED, ARCHIVED, DELETED},
    COMPLETED: {ARCHIVED, DELETED},
    ARCHIVED: {DELETED},
    DELETED: set(),
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


def is_hidden_from_inventory(status: str | None) -> bool:
    """Statuses that must never appear in switcher / active inventories."""
    normalized = (status or "").strip().upper()
    return normalized in {ARCHIVED, DELETED}