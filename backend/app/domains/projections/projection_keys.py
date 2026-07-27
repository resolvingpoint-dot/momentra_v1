"""Redis key builders for projection slices, versions, locks, and stale copies."""
from __future__ import annotations

from uuid import UUID

SLICE_TYPES = frozenset({"pulse", "moments", "memory", "life"})
PERSONAL_LIFE_TEMPLATE = "personal"


def normalize_template(template: str) -> str:
    raw = template.strip().replace("-", "_")
    if raw.lower() == PERSONAL_LIFE_TEMPLATE:
        return PERSONAL_LIFE_TEMPLATE
    return raw.upper()


def slice_key(user_id: UUID, template: str, slice_type: str) -> str:
    code = normalize_template(template)
    if slice_type == "life" and code == PERSONAL_LIFE_TEMPLATE:
        return f"projection:user:{user_id}:personal:life"
    return f"projection:user:{user_id}:{code}:{slice_type}"


def version_counter_key(user_id: UUID, template: str, slice_type: str) -> str:
    code = normalize_template(template)
    if slice_type == "life" and code == PERSONAL_LIFE_TEMPLATE:
        return f"projection:version:{user_id}:personal:life"
    return f"projection:version:{user_id}:{code}:{slice_type}"


def building_lock_key(user_id: UUID, template: str, slice_type: str) -> str:
    code = normalize_template(template)
    if slice_type == "life" and code == PERSONAL_LIFE_TEMPLATE:
        return f"projection:building:{user_id}:personal:life"
    return f"projection:building:{user_id}:{code}:{slice_type}"


def stale_key(user_id: UUID, template: str, slice_type: str) -> str:
    code = normalize_template(template)
    if slice_type == "life" and code == PERSONAL_LIFE_TEMPLATE:
        return f"projection:stale:{user_id}:personal:life"
    return f"projection:stale:{user_id}:{code}:{slice_type}"


def user_slice_prefix(user_id: UUID) -> str:
    return f"projection:user:{user_id}:"


def user_stale_prefix(user_id: UUID) -> str:
    return f"projection:stale:{user_id}:"


def user_version_prefix(user_id: UUID) -> str:
    return f"projection:version:{user_id}:"
