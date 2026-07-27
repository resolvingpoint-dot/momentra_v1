from __future__ import annotations

from pydantic import BaseModel


class EmptyStateConfig(BaseModel):
    """Partial, server-driven override for a module's empty state.

    Every field is optional: an override only carries the fields that should
    replace a client's local canonical copy. The static empty-state UI
    (illustrations, animations, default copy) ships inside each client, so the
    server does not need to send it on every launch.
    """

    illustration: str | None = None
    character_animation: str | None = None
    background_style: str | None = None
    color_accent: str | None = None
    color_surface: str | None = None
    color_bg: str | None = None
    primary_cta: str | None = None
    secondary_cta: str | None = None
    setup_steps: list[dict] | None = None
    learn_sections: list[dict] | None = None
    state_indicators: list[dict] | None = None


# Server-driven empty-state copy overrides, keyed by module key. Clients ship a
# local canonical copy; an entry here only carries the fields that should
# replace it, so copy can change without a new app build. Keep values partial —
# omit anything you don't intend to override.
EMPTY_STATE_OVERRIDES: dict[str, dict] = {
    "MY_MONEY": {
        "primary_cta": "Start your money journey",
        "secondary_cta": "See how it works",
    },
    "GROUP": {
        "primary_cta": "Start a Trip",
        "secondary_cta": "See how groups work",
        "setup_steps": [
            {"title": "Choose a shared type", "description": "Trip, purchase, or living."},
            {"title": "Invite your people", "description": "Bring the group together."},
            {"title": "Coordinate and remember", "description": "Plans, money, and memories in one place."},
        ],
        "learn_sections": [
            {"title": "Coordinate Together", "description": "Keep people, plans and money aligned."},
            {"title": "Manage Shared Money", "description": "Track contributions and spending."},
            {"title": "Remember Together", "description": "Capture milestones as they happen."},
        ],
        "state_indicators": [
            {"key": "empty", "label": "No group moments yet"},
        ],
    },
    "BUSINESS": {
        "primary_cta": "Create your first moment",
        "secondary_cta": "See how it works",
    },
}
