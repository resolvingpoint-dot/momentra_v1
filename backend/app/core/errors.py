"""Domain/application errors for the service layer.

Deliberately free of any HTTP/FastAPI imports so the service layer can raise
meaningful errors without depending on the web framework. The API layer maps
these to responses via the handlers registered in ``app.core.exceptions``.

Each error carries a machine-readable ``code`` and a ``status_code`` hint (a
plain integer) that the HTTP layer may use, but the service layer itself never
touches HTTP.
"""
from __future__ import annotations


class AppError(Exception):
    """Base class for domain/application errors."""

    status_code: int = 400
    code: str = "app_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: object | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    """Input failed a business/domain validation rule."""

    status_code = 422
    code = "validation_error"


class NotFoundError(AppError):
    """A requested entity does not exist (or is not visible to the actor)."""

    status_code = 404
    code = "not_found"


class PermissionDeniedError(AppError):
    """The actor is not allowed to perform the requested action."""

    status_code = 403
    code = "permission_denied"


class ConflictError(AppError):
    """The operation conflicts with the current state (e.g. uniqueness)."""

    status_code = 409
    code = "conflict"


class StateTransitionError(AppError):
    """An illegal workflow/state transition was attempted."""

    status_code = 409
    code = "lifecycle_transition_invalid"


class InvalidCurrencyError(AppError):
    """Currency code is invalid or unsupported."""

    status_code = 422
    code = "invalid_currency"


class AccountArchivedError(AppError):
    """Write attempted against an archived account."""

    status_code = 409
    code = "account_archived"


class DraftConflictError(AppError):
    """Concurrent draft mutation conflict."""

    status_code = 409
    code = "draft_conflict"


class ReferenceDataStaleError(AppError):
    """Client reference data version is stale."""

    status_code = 409
    code = "reference_data_stale"


class SnapshotRebuildingError(AppError):
    """Snapshot data is being rebuilt; client should retry."""

    status_code = 503
    code = "snapshot_rebuilding"


class TemplateNotRegisteredError(AppError):
    """No projection handler is registered for the requested moment type."""

    status_code = 501
    code = "template_not_registered"
