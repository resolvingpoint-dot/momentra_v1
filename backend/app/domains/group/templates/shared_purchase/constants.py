"""Shared Purchase template constants."""
from __future__ import annotations

from dataclasses import dataclass, field

MOMENT_TYPE = "SHARED_PURCHASE"

DEFAULT_QUICK_ADD_MODULES = [
    "CONTRIBUTORS",
    "PARTICIPANTS",
    "PURCHASE_ITEMS",
    "VENDORS",
    "EXPENSES",
    "POLLS",
    "UPDATES",
    "OWNERSHIP",
    "DELIVERY",
    "MEMORIES",
]


@dataclass(frozen=True)
class PurchaseProfileDefinition:
    code: str
    name: str
    pulse_readiness_title: str
    pulse_readiness_narrative: str
    quick_add_modules: list[str] = field(default_factory=lambda: list(DEFAULT_QUICK_ADD_MODULES))
    memory_prompts: list[str] = field(default_factory=lambda: ["Purchase highlight", "Funding milestone", "Delivery day"])


_PROFILES: dict[str, PurchaseProfileDefinition] = {
    "GIFT_POOL": PurchaseProfileDefinition(
        code="GIFT_POOL",
        name="Gift Pool",
        pulse_readiness_title="Let's fund this gift",
        pulse_readiness_narrative="Invite contributors and track progress toward your target.",
    ),
    "GROUP_PURCHASE": PurchaseProfileDefinition(
        code="GROUP_PURCHASE",
        name="Group Purchase",
        pulse_readiness_title="Let's make this purchase happen",
        pulse_readiness_narrative="Add contributors, compare vendors, and track spending.",
    ),
    "SHARED_ASSET": PurchaseProfileDefinition(
        code="SHARED_ASSET",
        name="Shared Asset",
        pulse_readiness_title="Your shared asset is taking shape",
        pulse_readiness_narrative="Define ownership and track contributions toward acquisition.",
    ),
    "CUSTOM_PURCHASE": PurchaseProfileDefinition(
        code="CUSTOM_PURCHASE",
        name="Custom Purchase",
        pulse_readiness_title="Your purchase is taking shape",
        pulse_readiness_narrative="Invite contributors and log the first activity.",
    ),
}


def get_purchase_profile(code: str | None) -> PurchaseProfileDefinition:
    if code and code in _PROFILES:
        return _PROFILES[code]
    return _PROFILES["GIFT_POOL"]
