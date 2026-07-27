from __future__ import annotations

import uuid

# Stable namespace so moment_type_id values are deterministic across restarts.
_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

PERSONAL_CONTEXT = "MY_MONEY"

# Legacy stored/API codes → canonical catalog code.
# TRIP is a group alias; included here so shared normalizers stay consistent.
LEGACY_MOMENT_TYPE_ALIASES: dict[str, str] = {
    "EMOTIONAL_SECURITY": "RELATIONSHIPS",
    "TRIP": "SHARED_EXPERIENCE",
}


class MomentType:
    def __init__(
        self,
        code: str,
        name: str,
        display_order: int,
        theme_color: str,
        icon_name: str,
        tagline: str,
    ) -> None:
        self.code = code
        self.name = name
        self.display_order = display_order
        self.theme_color = theme_color
        self.icon_name = icon_name
        self.tagline = tagline

    @property
    def type_id(self) -> str:
        return str(uuid.uuid5(_NAMESPACE, f"personal:{self.code}"))


MOMENT_TYPES: list[MomentType] = [
    MomentType(
        code="LIFE_OPERATIONS",
        name="Life Operations",
        display_order=1,
        theme_color="#4C6FFF",
        icon_name="bolt",
        tagline=(
            "Build the foundation for everyday life with routines, "
            "responsibilities and essential activities."
        ),
    ),
    MomentType(
        code="FUTURE_BUILDING",
        name="Future Building",
        display_order=2,
        theme_color="#22C55E",
        icon_name="rocket",
        tagline="Plan the milestones, habits and achievements that shape your future.",
    ),
    MomentType(
        code="LIFESTYLE",
        name="Lifestyle",
        display_order=3,
        theme_color="#F59E0B",
        icon_name="sparkles",
        tagline="Capture the experiences, hobbies and moments that make life enjoyable.",
    ),
    MomentType(
        code="RELATIONSHIPS",
        name="Emotional Security",
        display_order=4,
        theme_color="#EC4899",
        icon_name="heart",
        tagline=(
            "Strengthen the relationships and support systems that help you "
            "feel connected and secure."
        ),
    ),
]

MOMENT_TYPES_BY_CODE: dict[str, MomentType] = {mt.code: mt for mt in MOMENT_TYPES}


def normalize_moment_type_code(code: str | None) -> str:
    """Prefer shared Quick Add contract aliases; keep local table as fallback."""
    if not code:
        return ""
    try:
        from app.domains.quick_add_contract.aliases import (
            normalize_moment_type_code as _contract_normalize,
        )

        return _contract_normalize(code)
    except Exception:
        return LEGACY_MOMENT_TYPE_ALIASES.get(code, code)


def moment_type_id(code: str) -> str:
    canonical = normalize_moment_type_code(code)
    mt = MOMENT_TYPES_BY_CODE.get(canonical)
    if mt is not None:
        return mt.type_id
    return str(uuid.uuid5(_NAMESPACE, f"personal:{canonical}"))


def legacy_moment_type_id(code: str) -> str:
    """Deterministic id for a raw code (including legacy aliases)."""
    return str(uuid.uuid5(_NAMESPACE, f"personal:{code}"))


def moment_type_name(code: str) -> str:
    canonical = normalize_moment_type_code(code)
    mt = MOMENT_TYPES_BY_CODE.get(canonical)
    return mt.name if mt else canonical.replace("_", " ").title()
