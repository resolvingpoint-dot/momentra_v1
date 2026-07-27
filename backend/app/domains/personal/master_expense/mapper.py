"""Map master expense payloads to template quick-add bodies."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.domains.personal.master_expense.schemas import (
    MasterExpenseCreateRequest,
    MasterExpenseExperienceInput,
    MasterExpenseSharedInput,
)

FEELING_TO_ENERGY: dict[str, str] = {
    "VERY_BAD": "Drained",
    "BAD": "Drained",
    "NEUTRAL": "Neutral",
    "GOOD": "Refreshed",
    "GREAT": "Energized",
}

MEANINGFULNESS_TO_QUALITY: dict[str, str] = {
    "LOW": "Ordinary",
    "MEDIUM": "Enjoyable",
    "HIGH": "Memorable",
}

MEMORABILITY_TO_QUALITY: dict[str, str] = {
    "LOW": "Ordinary",
    "MEDIUM": "Enjoyable",
    "HIGH": "Exceptional",
}

CONTEXT_TO_EXPERIENCE_TYPE: dict[str, str] = {
    "CELEBRATION": "Celebration",
    "DAILY_NEED": "Food",
    "GIFT": "Other",
    "TRAVEL": "Travel",
    "OTHER": "Other",
}

SHARED_WITH_TO_RELATIONSHIP: dict[str, str] = {
    "SPOUSE": "Partner",
    "PARENTS": "Parent",
    "FAMILY": "Family",
    "FRIENDS": "Friend",
    "CUSTOM": "Friend",
}

IMPACT_TO_VALUE: dict[str, str] = {
    "STRENGTHENED_CONNECTION": "Relationship Building",
    "CELEBRATION_TOGETHER": "Excellent Value",
    "SUPPORT_GIVEN": "Life Enriching",
}


def _upper(value: str | None) -> str:
    return str(value or "").strip().upper()


def normalize_legacy_body(body: dict[str, Any]) -> dict[str, Any]:
    """Accept legacy nested mobile/web payloads and flat orchestrator payloads."""
    if body.get("title") and body.get("amount_minor") is not None:
        return dict(body)

    expense = body.get("expense") or {}
    experience = body.get("experience") or {}
    shared_legacy = body.get("shared_experience") or body.get("shared") or {}
    context = body.get("context") or {}

    amount_minor = expense.get("amount_minor")
    amount_legacy = expense.get("amount")

    shared_with = shared_legacy.get("shared_with") or []
    relationship_impact = shared_legacy.get("relationship_impact")
    impacts: list[str] = []
    if isinstance(relationship_impact, list):
        impacts = [str(v) for v in relationship_impact]
    elif relationship_impact:
        impacts = [str(relationship_impact)]

    is_shared = bool(shared_legacy.get("is_shared", shared_legacy.get("enabled", False)))

    return {
        "client_request_id": body.get("client_request_id"),
        "title": expense.get("title") or expense.get("description") or "",
        "amount_minor": amount_minor,
        "amount": amount_legacy,
        "currency_code": expense.get("currency_code"),
        "account_id": expense.get("account_id"),
        "category_code": expense.get("category_code"),
        "category_name": expense.get("category_name"),
        "subcategory_code": expense.get("subcategory_code")
        or expense.get("subcategory")
        or expense.get("sub_category")
        or expense.get("expense_subcategory"),
        "occurred_at": expense.get("transaction_date") or expense.get("occurred_at"),
        "experience": experience,
        "shared": {
            "is_shared": is_shared,
            "shared_with": shared_with,
            "relationship_impact": impacts,
        },
        "context": context,
        "notes": body.get("notes"),
    }


def parse_occurred_at(raw: str | None, *, fallback: datetime) -> datetime:
    if not raw:
        return fallback
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is not None:
            return parsed.astimezone().replace(tzinfo=None)
        return parsed
    except ValueError:
        return fallback


def experience_quality(experience: MasterExpenseExperienceInput | None) -> str:
    if experience is None:
        return "Enjoyable"
    memorability = _upper(experience.memorability)
    if memorability in MEMORABILITY_TO_QUALITY:
        return MEMORABILITY_TO_QUALITY[memorability]
    meaningfulness = _upper(experience.meaningfulness)
    return MEANINGFULNESS_TO_QUALITY.get(meaningfulness, "Enjoyable")


def build_life_operations_body(
    req: MasterExpenseCreateRequest,
    *,
    master_expense_id: UUID,
    validated_expense: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event_type": "EXPENSE",
        "event_title": req.title,
        "source": "MASTER_EXPENSE",
        "master_expense_id": str(master_expense_id),
        "expense": {
            **validated_expense,
            "title": req.title,
            "notes": req.notes,
            "source": "MASTER_EXPENSE",
        },
        "notes": req.notes,
    }


def build_lifestyle_body(
    req: MasterExpenseCreateRequest,
    *,
    master_expense_id: UUID,
    validated_expense: dict[str, Any],
) -> dict[str, Any]:
    experience = req.experience or MasterExpenseExperienceInput()
    context_reason = _upper(req.context.reason if req.context else None)
    feeling = _upper(experience.feeling)

    return {
        "event_type": "EXPERIENCE",
        "event_title": req.title,
        "source": "MASTER_EXPENSE",
        "master_expense_id": str(master_expense_id),
        "lifestyle": {
            "experience_type": CONTEXT_TO_EXPERIENCE_TYPE.get(context_reason, "Other"),
            "experience_quality": experience_quality(experience),
            "energy_impact": FEELING_TO_ENERGY.get(feeling, "Neutral"),
            "value_received": "Worth It",
            "notes": req.notes,
            "amount_minor": validated_expense["amount_minor"],
            "currency_code": validated_expense["currency_code"],
            "context_reason": context_reason or None,
            "feeling": feeling or None,
            "meaningfulness": _upper(experience.meaningfulness) or None,
            "memorability": _upper(experience.memorability) or None,
        },
        "notes": req.notes,
    }


def build_relationships_body(
    req: MasterExpenseCreateRequest,
    *,
    master_expense_id: UUID,
    validated_expense: dict[str, Any],
    shared: MasterExpenseSharedInput,
) -> dict[str, Any]:
    context_reason = _upper(req.context.reason if req.context else None)
    shared_codes = [_upper(code) for code in shared.shared_with if str(code).strip()]
    primary_shared = shared_codes[0] if shared_codes else "FRIENDS"
    impacts = [_upper(code) for code in shared.relationship_impact if str(code).strip()]
    primary_impact = impacts[0] if impacts else "STRENGTHENED_CONNECTION"

    return {
        "event_type": "SHARED_EXPERIENCE",
        "event_title": req.title,
        "source": "MASTER_EXPENSE",
        "master_expense_id": str(master_expense_id),
        "relationships": {
            "experience_type": CONTEXT_TO_EXPERIENCE_TYPE.get(context_reason, "Celebration"),
            "relationship_type": SHARED_WITH_TO_RELATIONSHIP.get(primary_shared, "Friend"),
            "value_received": IMPACT_TO_VALUE.get(primary_impact, "Relationship Building"),
            "shared_with": shared_codes,
            "relationship_impact": impacts,
            "notes": req.notes,
            "amount_minor": validated_expense["amount_minor"],
            "currency_code": validated_expense["currency_code"],
            "account_id": validated_expense["account_id"],
        },
        "expense": validated_expense,
        "notes": req.notes,
    }


def legacy_event_refs(
    *,
    life_ops_id: UUID | None,
    lifestyle_id: UUID | None,
    relationships_id: UUID | None,
    life_ops_moment_id: UUID,
    lifestyle_moment_id: UUID,
    relationships_moment_id: UUID | None,
) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    if life_ops_id is not None:
        refs.append(
            {
                "quick_add_event_id": str(life_ops_id),
                "moment_id": str(life_ops_moment_id),
                "moment_type_code": "LIFE_OPERATIONS",
                "event_type": "EXPENSE",
            }
        )
    if lifestyle_id is not None:
        refs.append(
            {
                "quick_add_event_id": str(lifestyle_id),
                "moment_id": str(lifestyle_moment_id),
                "moment_type_code": "LIFESTYLE",
                "event_type": "EXPERIENCE",
            }
        )
    if relationships_id is not None and relationships_moment_id is not None:
        refs.append(
            {
                "quick_add_event_id": str(relationships_id),
                "moment_id": str(relationships_moment_id),
                "moment_type_code": "RELATIONSHIPS",
                "event_type": "SHARED_EXPERIENCE",
            }
        )
    return refs
