"""Patchable fields per action type."""
from __future__ import annotations

from app.domains.business.activity.types import ActionType

_ALWAYS_PATCHABLE = {"title", "subtitle"}

_ACTION_PATCHABLE: dict[ActionType, set[str]] = {
    ActionType.TEAM_UPDATE: {"description", "activity_status", "priority", "category"},
    ActionType.ISSUE: {"description", "severity", "resolution_status"},
    ActionType.ESCALATION: {"severity", "status", "notes"},
    ActionType.MEETING: {"title", "meeting_at", "notes"},
    ActionType.MEMBER_UPDATE: {"update_kind", "notes"},
    ActionType.NOTE: {"title", "subtitle"},
    ActionType.CASH_INFLOW: {"amount", "currency", "inflow_type", "description", "reference"},
    ActionType.EXPENSE_BURN: {"amount", "currency", "expense_category", "description"},
    ActionType.RUNWAY_RISK: {"severity", "risk_status", "description"},
    ActionType.STRATEGIC_DECISION: {"decision_status", "description"},
    ActionType.SPEND_ENTRY: {"amount", "amount_minor", "currency", "currency_code", "spend_category", "description"},
    ActionType.VENDOR_UPDATE: {"vendor_status", "impact_level", "description"},
    ActionType.ISSUE_RISK: {"title", "subtitle", "description", "severity", "issue_status", "status", "impact_area"},
    ActionType.OPERATIONAL_IMPROVEMENT: {"improvement_status", "description"},
}


def patchable_fields(action_type: ActionType) -> set[str]:
    return _ALWAYS_PATCHABLE | _ACTION_PATCHABLE.get(action_type, set())


def filter_patch(action_type: ActionType, patch: dict) -> dict:
    allowed = patchable_fields(action_type)
    return {k: v for k, v in patch.items() if k in allowed}
