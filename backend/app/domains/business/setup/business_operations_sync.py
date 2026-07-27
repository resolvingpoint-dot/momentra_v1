"""Upsert Business Operations specialty tables for the same shared moment UUID."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import (
    BusinessOperationsBudgetCategories,
    BusinessOperationsGovernanceRules,
    BusinessOperationsSetup,
    BusinessOperationsStructure,
)
from app.domains.business.setup.business_operations_mappers import model_to_sql, scope_to_sql
from app.domains.business.setup.runway_mappers import minor_to_major


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def upsert_operations_setup(
    session: AsyncSession,
    *,
    moment_id: UUID,
    owner_user_id: UUID,
    answers: dict[str, Any],
) -> None:
    currency = (answers.get("operating_currency_code") or "INR").upper()
    budget_minor = answers.get("monthly_budget_minor")
    budget_minor_i = int(budget_minor) if budget_minor is not None else 0
    scope = answers.get("operations_scope")
    model = answers.get("operating_model")
    extras = {
        "moment_name": answers.get("moment_name"),
        "operations_owner_id": str(owner_user_id),
        "allow_multi_currency": answers.get("allow_multi_currency"),
        "default_currency_code": answers.get("default_currency_code"),
        "financial_year_start": answers.get("financial_year_start"),
        "allocation_mode": answers.get("allocation_mode"),
        "allow_overallocation": answers.get("allow_overallocation"),
    }
    now = _now()
    payload = {
        # Legacy NOT NULL mirrors (compatibility)
        "operations_type": scope_to_sql(scope),
        "operating_model": model_to_sql(model),
        "operational_owner_role": "Business Owner",
        "operating_currency": currency,
        "monthly_operating_budget": minor_to_major(budget_minor_i, currency),
        # Canonical columns
        "operations_name": answers.get("operations_name") or answers.get("moment_name"),
        "operations_scope": scope,
        "operating_model_canonical": model,
        "monthly_budget_minor": int(budget_minor) if budget_minor is not None else None,
        "review_cycle": answers.get("review_cycle"),
        "financial_year_start": answers.get("financial_year_start"),
        "country_code": answers.get("country_code"),
        "locale": answers.get("locale"),
        "timezone": answers.get("timezone"),
        "setup_extras": extras,
        "updated_at": now,
    }
    result = await session.execute(
        select(BusinessOperationsSetup).where(BusinessOperationsSetup.moment_id == moment_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(BusinessOperationsSetup(moment_id=moment_id, created_at=now, **payload))
    else:
        for k, v in payload.items():
            setattr(row, k, v)
    await session.flush()


async def upsert_operations_structure(
    session: AsyncSession,
    *,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    vendor_level = answers.get("vendor_dependency_level")
    approval_model = answers.get("approval_model")
    issue_sensitivity = answers.get("issue_sensitivity")
    monitoring = answers.get("monitoring_level")
    review_cycle = answers.get("review_cycle")
    allocations = answers.get("budget_allocations") or []
    categories = answers.get("budget_categories") or []
    alert_conditions = answers.get("alert_conditions") if isinstance(answers.get("alert_conditions"), dict) else {}
    now = _now()
    extras = {
        "allow_overallocation": answers.get("allow_overallocation"),
        "allow_multi_currency": answers.get("allow_multi_currency"),
        "default_currency_code": answers.get("default_currency_code"),
        "approval_owner_id": answers.get("approval_owner_id"),
        "escalation_contact_id": answers.get("escalation_contact_id"),
    }
    payload = {
        # Legacy mirror: lowercase vendor dependency
        "vendor_dependency": str(vendor_level).lower() if vendor_level else None,
        # Canonical string in approval_model column
        "approval_model": approval_model,
        "issue_sensitivity": issue_sensitivity,
        "performance_review_cycle": str(review_cycle).lower() if review_cycle else None,
        "kpi_tracking": {"enabled": bool(answers.get("activate_monitoring", True))},
        "vendor_dependency_level": vendor_level,
        "monitoring_level_canonical": monitoring,
        "allocation_mode": answers.get("allocation_mode"),
        "budget_allocations": {"allocations": allocations} if isinstance(allocations, list) else allocations,
        "budget_categories": {"categories": categories} if isinstance(categories, list) else categories,
        "alert_conditions": alert_conditions,
        "structure_extras": extras,
        "updated_at": now,
    }
    result = await session.execute(
        select(BusinessOperationsStructure).where(BusinessOperationsStructure.moment_id == moment_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(BusinessOperationsStructure(moment_id=moment_id, created_at=now, **payload))
    else:
        for k, v in payload.items():
            setattr(row, k, v)
    await session.flush()


async def upsert_operations_governance(
    session: AsyncSession,
    *,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    approval_required = bool(
        answers.get("approval_required_for_spend")
        or answers.get("approval_required_for_vendor_changes")
        or answers.get("approval_required_for_budget_changes")
        or answers.get("approval_required_for_issue_closure")
        or (answers.get("approval_model") and answers.get("approval_model") != "NONE")
    )
    vis = answers.get("operational_visibility") or answers.get("visibility") or "TEAM"
    prefs = (
        answers.get("notification_preferences")
        if isinstance(answers.get("notification_preferences"), dict)
        else {}
    )
    monitoring = answers.get("monitoring_level") or "STANDARD"
    secondary = answers.get("secondary_approver_ids") or []
    alert_ids = answers.get("alert_recipient_ids") or []
    now = _now()
    extras = {
        "approval_required_for_spend": answers.get("approval_required_for_spend"),
        "approval_required_for_vendor_changes": answers.get("approval_required_for_vendor_changes"),
        "approval_required_for_budget_changes": answers.get("approval_required_for_budget_changes"),
        "approval_required_for_issue_closure": answers.get("approval_required_for_issue_closure"),
        "approval_owner_id": answers.get("approval_owner_id"),
        "escalation_contact_id": answers.get("escalation_contact_id"),
        "approval_model": answers.get("approval_model"),
        "invite_on_activation": answers.get("invite_on_activation"),
        "notify_members": answers.get("notify_members"),
        "activate_monitoring": answers.get("activate_monitoring"),
        "notification_preferences": prefs,
    }
    payload = {
        "visibility_roles": {"visibility": vis},
        "alert_conditions": answers.get("alert_conditions")
        if isinstance(answers.get("alert_conditions"), dict)
        else {},
        "alert_recipient_roles": {"roles": ["OWNER", "OPERATIONS_LEAD", "BUDGET_CONTROLLER"]},
        "approval_required": approval_required,
        "monitoring_level": str(monitoring).lower(),
        "approval_rules": {
            "approval_model": answers.get("approval_model"),
            "approval_owner_id": answers.get("approval_owner_id"),
            "approval_threshold_minor": answers.get("approval_threshold_minor"),
            "approval_required_for_spend": answers.get("approval_required_for_spend"),
            "approval_required_for_vendor_changes": answers.get(
                "approval_required_for_vendor_changes"
            ),
            "approval_required_for_budget_changes": answers.get(
                "approval_required_for_budget_changes"
            ),
            "approval_required_for_issue_closure": answers.get(
                "approval_required_for_issue_closure"
            ),
        },
        "approval_threshold_minor": answers.get("approval_threshold_minor"),
        "secondary_approver_ids": {"ids": secondary} if isinstance(secondary, list) else secondary,
        "alert_recipient_ids": {"ids": alert_ids} if isinstance(alert_ids, list) else alert_ids,
        "visibility": vis,
        "governance_extras": extras,
        "updated_at": now,
    }
    result = await session.execute(
        select(BusinessOperationsGovernanceRules).where(
            BusinessOperationsGovernanceRules.moment_id == moment_id
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(
            BusinessOperationsGovernanceRules(moment_id=moment_id, created_at=now, **payload)
        )
    else:
        for k, v in payload.items():
            setattr(row, k, v)
    await session.flush()


async def upsert_budget_allocations(
    session: AsyncSession,
    *,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    """Upsert BusinessOperationsBudgetCategories keyed by allocation_id."""
    currency = (answers.get("operating_currency_code") or "INR").upper()
    allocations = answers.get("budget_allocations") or []
    if not isinstance(allocations, list):
        return

    result = await session.execute(
        select(BusinessOperationsBudgetCategories).where(
            BusinessOperationsBudgetCategories.moment_id == moment_id
        )
    )
    try:
        existing = list(result.scalars().all())
    except Exception:
        existing = []
    by_allocation = {
        str(r.allocation_id): r for r in existing if getattr(r, "allocation_id", None)
    }

    now = _now()
    for raw in allocations:
        if not isinstance(raw, dict):
            continue
        aid = str(raw.get("allocation_id") or "")
        if not aid:
            continue
        amount_minor = int(raw.get("amount_minor") or 0)
        label = str(raw.get("label") or raw.get("category_code") or "Allocation")[:100]
        code = str(raw.get("category_code") or "custom")[:64]
        pct = raw.get("percentage")
        payload = {
            "category_name": label,
            "custom_category_name": label if len(str(raw.get("label") or "")) > 100 else None,
            "allocated_budget": minor_to_major(amount_minor, currency),
            "allocated_budget_minor": amount_minor,
            "currency": currency,
            "category_status": "active",
            "allocation_id": aid,
            "percentage": int(pct) if pct is not None else None,
            "category_code": code,
            "updated_at": now,
            "archived_at": None,
        }
        row = by_allocation.get(aid)
        if row is None:
            session.add(
                BusinessOperationsBudgetCategories(
                    moment_id=moment_id,
                    created_at=now,
                    **payload,
                )
            )
        else:
            for k, v in payload.items():
                setattr(row, k, v)

    await session.flush()
