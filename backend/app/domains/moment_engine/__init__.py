"""Moment lifecycle orchestration for all contexts.

Every moment create / update / activate / pause / complete / archive should
eventually flow through :class:`MomentEngine`. Context-specific persistence is
provided by adapters; side-effects (snapshot refresh, memory, analytics) are
published as domain events and handled asynchronously via Celery.
"""

from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.handlers import register_moment_handlers
from app.domains.moment_engine.registry import get_domain_registry, register_default_domains
from app.domains.moment_engine.templates import register_default_templates

__all__ = [
    "MomentEngine",
    "get_domain_registry",
    "register_default_domains",
    "register_default_templates",
    "register_moment_handlers",
]
