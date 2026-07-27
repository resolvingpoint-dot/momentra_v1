from app.domains.moment_engine.handlers.moment_created import register_moment_created_handlers
from app.domains.moment_engine.handlers.moment_lifecycle import register_lifecycle_handlers

_registered = False


def register_moment_handlers() -> None:
    """Wire all moment-engine domain event handlers (idempotent)."""
    global _registered
    if _registered:
        return
    register_moment_created_handlers()
    register_lifecycle_handlers()
    _registered = True
