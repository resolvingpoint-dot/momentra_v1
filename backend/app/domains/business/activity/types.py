"""Business activity action-type enumerations."""
from __future__ import annotations

from enum import Enum


class ActionType(str, Enum):
    # Team Operations (10)
    TEAM_UPDATE = "TEAM_UPDATE"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    ISSUE = "ISSUE"
    RECOGNITION = "RECOGNITION"
    ESCALATION = "ESCALATION"
    REVIEW = "REVIEW"
    PARTICIPATION = "PARTICIPATION"
    MEETING = "MEETING"
    MEMBER_UPDATE = "MEMBER_UPDATE"
    NOTE = "NOTE"

    # Business Runway (5)
    CASH_INFLOW = "CASH_INFLOW"
    EXPENSE_BURN = "EXPENSE_BURN"
    RUNWAY_RISK = "RUNWAY_RISK"
    STRATEGIC_DECISION = "STRATEGIC_DECISION"
    FINANCIAL_UPDATE = "FINANCIAL_UPDATE"

    # Business Operations (6)
    SPEND_ENTRY = "SPEND_ENTRY"
    VENDOR_UPDATE = "VENDOR_UPDATE"
    OPS_APPROVAL_REQUEST = "OPS_APPROVAL_REQUEST"
    ISSUE_RISK = "ISSUE_RISK"
    OPERATIONAL_IMPROVEMENT = "OPERATIONAL_IMPROVEMENT"
    OPS_GENERAL_UPDATE = "OPS_GENERAL_UPDATE"


TEAM_OPERATIONS_ACTIONS: frozenset[ActionType] = frozenset({
    ActionType.TEAM_UPDATE,
    ActionType.APPROVAL_REQUEST,
    ActionType.ISSUE,
    ActionType.RECOGNITION,
    ActionType.ESCALATION,
    ActionType.REVIEW,
    ActionType.PARTICIPATION,
    ActionType.MEETING,
    ActionType.MEMBER_UPDATE,
    ActionType.NOTE,
})

BUSINESS_RUNWAY_ACTIONS: frozenset[ActionType] = frozenset({
    ActionType.CASH_INFLOW,
    ActionType.EXPENSE_BURN,
    ActionType.RUNWAY_RISK,
    ActionType.STRATEGIC_DECISION,
    ActionType.FINANCIAL_UPDATE,
})

BUSINESS_OPERATIONS_ACTIONS: frozenset[ActionType] = frozenset({
    ActionType.SPEND_ENTRY,
    ActionType.VENDOR_UPDATE,
    ActionType.OPS_APPROVAL_REQUEST,
    ActionType.ISSUE_RISK,
    ActionType.OPERATIONAL_IMPROVEMENT,
    ActionType.OPS_GENERAL_UPDATE,
})


def moment_type_for_action(action: ActionType) -> str:
    if action in TEAM_OPERATIONS_ACTIONS:
        return "TEAM_OPERATIONS"
    if action in BUSINESS_RUNWAY_ACTIONS:
        return "BUSINESS_RUNWAY"
    if action in BUSINESS_OPERATIONS_ACTIONS:
        return "BUSINESS_OPERATIONS"
    return "TEAM_OPERATIONS"
