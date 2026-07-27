"""Quick Add v1 contract: normalizers, registry validator, handler lifecycle."""

from app.domains.quick_add_contract.aliases import (
    ACTION_ID_ALIASES,
    MOMENT_TYPE_ALIASES,
    PAYER_FIELD_ALIASES,
    normalize_action_id,
    normalize_moment_type_code,
)
from app.domains.quick_add_contract.errors import (
    QuickAddActionNotSupported,
    QuickAddContractError,
    QuickAddInvalidPayload,
)
from app.domains.quick_add_contract.hash import compute_registry_hash, load_reference_actions
from app.domains.quick_add_contract.normalize import normalize_payload
from app.domains.quick_add_contract.validator import QuickAddRegistryValidator, validate_reference_registry

__all__ = [
    "ACTION_ID_ALIASES",
    "MOMENT_TYPE_ALIASES",
    "PAYER_FIELD_ALIASES",
    "QuickAddActionNotSupported",
    "QuickAddContractError",
    "QuickAddInvalidPayload",
    "QuickAddRegistryValidator",
    "compute_registry_hash",
    "load_reference_actions",
    "normalize_action_id",
    "normalize_moment_type_code",
    "normalize_payload",
    "validate_reference_registry",
]
