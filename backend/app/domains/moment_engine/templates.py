from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MomentTemplate:
    """Defaults and refresh policy for a (context, moment_type) pair.

    ``moment_type`` may be ``None`` to act as the context-wide fallback.
    """

    context: str
    moment_type: str | None = None
    initial_status: str = "DRAFT"
    initial_setup_state: str = "EMPTY"
    worker_context: str = "personal"  # memory/analytics procedure key
    refresh_on_create: bool = True
    refresh_on_activate: bool = True
    refresh_on_update: bool = False
    refresh_on_pause: bool = False
    refresh_on_complete: bool = True
    refresh_on_archive: bool = False
    extra_create_defaults: dict[str, Any] = field(default_factory=dict)


class TemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str | None], MomentTemplate] = {}

    def register(self, template: MomentTemplate) -> None:
        self._templates[(template.context, template.moment_type)] = template

    def resolve(self, context: str, moment_type: str | None) -> MomentTemplate:
        key = (context, moment_type)
        if key in self._templates:
            return self._templates[key]
        fallback = self._templates.get((context, None))
        if fallback is not None:
            return fallback
        # Safe default for contexts not yet registered.
        return MomentTemplate(context=context, moment_type=moment_type)


_registry = TemplateRegistry()


def get_template_registry() -> TemplateRegistry:
    return _registry


def register_default_templates() -> None:
    """Deprecated — use :func:`registry.register_default_domains`."""
    from app.domains.moment_engine.registry import register_default_domains

    register_default_domains()
