"""Shared template tab projections (life, memory) reusable across personal templates."""

from app.domains.personal.templates.shared_projection.base_handler import BaseTemplateHandler
from app.domains.personal.templates.shared_projection.handler import SharedTemplateHandler
from app.domains.personal.templates.shared_projection.life_mapper import build_life_operating_view
from app.domains.personal.templates.shared_projection.memory_mapper import build_memory_projection

__all__ = [
    "BaseTemplateHandler",
    "SharedTemplateHandler",
    "build_life_operating_view",
    "build_memory_projection",
]
