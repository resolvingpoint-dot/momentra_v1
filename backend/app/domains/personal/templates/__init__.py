"""Personal template tab projection handlers."""

from app.domains.personal.templates.registry import (
    get_template_projection_registry,
    register_template_projection_handlers,
)

__all__ = [
    "get_template_projection_registry",
    "register_template_projection_handlers",
]
