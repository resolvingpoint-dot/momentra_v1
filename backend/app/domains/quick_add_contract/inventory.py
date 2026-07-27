"""Known backend handler / renderer / builder IDs for reference actions."""
from __future__ import annotations

# Declared inventory for QuickAddRegistryValidator (tests assert presence).
BACKEND_HANDLER_IDS: frozenset[str] = frozenset(
    {
        "personal.life_operations.ExpenseHandler",
        "personal.future_building.ContributionHandler",
        "personal.lifestyle.ExperienceHandler",
        "personal.relationships.ConnectionHandler",
        "group.trip.TripDeepService.create_expense",
        "group.purchase.purchase_quick_add_create",
        "group.living.living_quick_add_create",
    }
)

BACKEND_RENDERER_IDS: frozenset[str] = frozenset(
    {
        "personal.life_operations.expense",
        "personal.future_building.contribution",
        "personal.lifestyle.experience",
        "personal.relationships.connection",
        "experience.expense",
        "purchase.contribution",
        "living.rent",
    }
)

BACKEND_PAYLOAD_BUILDER_IDS: frozenset[str] = frozenset(
    {
        "personal.life_operations.expense",
        "personal.future_building.contribution",
        "personal.lifestyle.experience",
        "personal.relationships.connection",
        "group.experience.expense",
        "group.purchase.contributor",
        "group.living.rent",
    }
)
