"""Central authorization facade — shared by REST, workers, and future GraphQL."""
from __future__ import annotations

from app.authorization.require import ResourceRef, require

__all__ = ["ResourceRef", "require"]
