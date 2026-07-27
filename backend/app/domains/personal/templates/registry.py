"""Registry mapping moment_type_code -> tab projection handler."""
from __future__ import annotations

from app.core.errors import TemplateNotRegisteredError
from app.domains.personal.templates.base import TemplateProjectionHandler


class TemplateProjectionRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, TemplateProjectionHandler] = {}

    def register(self, handler: TemplateProjectionHandler) -> None:
        code = handler.moment_type_code.upper()
        self._handlers[code] = handler

    def resolve(self, moment_type_code: str) -> TemplateProjectionHandler:
        code = moment_type_code.strip().upper().replace("-", "_")
        handler = self._handlers.get(code)
        if handler is None:
            raise TemplateNotRegisteredError(
                f"No template projection handler registered for {code}",
                code="template_not_registered",
            )
        return handler

    def is_registered(self, moment_type_code: str) -> bool:
        code = moment_type_code.strip().upper().replace("-", "_")
        return code in self._handlers


_registry = TemplateProjectionRegistry()


def get_template_projection_registry() -> TemplateProjectionRegistry:
    return _registry


def register_template_projection_handlers() -> None:
    """Register all personal template projection handlers (idempotent)."""
    from app.domains.personal.templates.future_building.handler import (
        FutureBuildingTemplateHandler,
    )
    from app.domains.personal.templates.life_operations.handler import (
        LifeOperationsTemplateHandler,
    )
    from app.domains.personal.templates.lifestyle.handler import (
        LifestyleTemplateHandler,
    )
    from app.domains.personal.templates.relationships.handler import (
        RelationshipsTemplateHandler,
    )

    registry = get_template_projection_registry()
    for handler in (
        LifeOperationsTemplateHandler(),
        FutureBuildingTemplateHandler(),
        LifestyleTemplateHandler(),
        RelationshipsTemplateHandler(),
    ):
        if not registry.is_registered(handler.moment_type_code):
            registry.register(handler)
