"""AuthN platform facade — Principal + dependencies wrapping existing auth."""
from __future__ import annotations

from app.auth.principal import Principal, principal_from_auth
from app.auth.dependencies import get_current_principal

__all__ = [
    "Principal",
    "principal_from_auth",
    "get_current_principal",
]
