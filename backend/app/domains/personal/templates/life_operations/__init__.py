"""Life Operations template projection package."""

from app.domains.personal.templates.life_operations.setup_schema import (
    LIFE_OPERATIONS_TEMPLATE_CONTRACT,
    upsert_life_operations_profile,
)

__all__ = [
    "LIFE_OPERATIONS_TEMPLATE_CONTRACT",
    "upsert_life_operations_profile",
]
