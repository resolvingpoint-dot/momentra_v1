"""ACTION_REGISTRY — frozen mapping from ActionType to handler metadata."""
from __future__ import annotations

from types import MappingProxyType

from app.domains.business.activity.types import ActionType

_REGISTRY: dict[ActionType, dict] = {
    # ---- Team Operations -------------------------------------------------- #
    ActionType.TEAM_UPDATE: {
        "handler": "app.domains.business.activity.handlers.team_operations.team_update",
        "permission": None,
        "typed_table": "team_activities",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.APPROVAL_REQUEST: {
        "handler": "app.domains.business.activity.handlers.team_operations.approval_request",
        "permission": None,
        "typed_table": "team_approval_requests",
        "affected_slices": ("pulse", "moments"),
        "editable": False,
        "deletable": False,
    },
    ActionType.ISSUE: {
        "handler": "app.domains.business.activity.handlers.team_operations.issue",
        "permission": None,
        "typed_table": "team_issue_risks",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.RECOGNITION: {
        "handler": "app.domains.business.activity.handlers.team_operations.recognition",
        "permission": None,
        "typed_table": "team_recognitions",
        "affected_slices": ("pulse", "moments"),
        "editable": False,
        "deletable": True,
    },
    ActionType.ESCALATION: {
        "handler": "app.domains.business.activity.handlers.team_operations.escalation",
        "permission": None,
        "typed_table": "team_escalations",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.REVIEW: {
        "handler": "app.domains.business.activity.handlers.team_operations.review",
        "permission": None,
        "typed_table": None,
        "affected_slices": ("pulse", "moments"),
        "editable": False,
        "deletable": False,
    },
    ActionType.PARTICIPATION: {
        "handler": "app.domains.business.activity.handlers.team_operations.participation",
        "permission": None,
        "typed_table": "team_participation",
        "affected_slices": ("pulse", "moments"),
        "editable": False,
        "deletable": True,
    },
    ActionType.MEETING: {
        "handler": "app.domains.business.activity.handlers.team_operations.meeting",
        "permission": None,
        "typed_table": "team_meetings",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.MEMBER_UPDATE: {
        "handler": "app.domains.business.activity.handlers.team_operations.member_update",
        "permission": None,
        "typed_table": "team_member_updates",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.NOTE: {
        "handler": "app.domains.business.activity.handlers.team_operations.note",
        "permission": None,
        "typed_table": None,
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    # ---- Business Runway ------------------------------------------------- #
    ActionType.CASH_INFLOW: {
        "handler": "app.domains.business.activity.handlers.business_runway.cash_inflow",
        "permission": "can_add_runway_transactions",
        "typed_table": "runway_cash_inflows",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.EXPENSE_BURN: {
        "handler": "app.domains.business.activity.handlers.business_runway.expense_burn",
        "permission": "can_add_runway_transactions",
        "typed_table": "runway_expense_burns",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.RUNWAY_RISK: {
        "handler": "app.domains.business.activity.handlers.business_runway.runway_risk",
        "permission": "can_add_runway_transactions",
        "typed_table": "runway_risks",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.STRATEGIC_DECISION: {
        "handler": "app.domains.business.activity.handlers.business_runway.strategic_decision",
        "permission": "can_add_runway_transactions",
        "typed_table": "runway_strategic_decisions",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.FINANCIAL_UPDATE: {
        "handler": "app.domains.business.activity.handlers.business_runway.financial_update",
        "permission": "can_edit_financial_entries",
        "typed_table": "runway_financial_updates",
        "affected_slices": ("pulse", "moments"),
        "editable": False,
        "deletable": False,
    },
    # ---- Business Operations --------------------------------------------- #
    ActionType.SPEND_ENTRY: {
        "handler": "app.domains.business.activity.handlers.business_operations.spend_entry",
        "permission": "can_add_operations_records",
        "typed_table": "operations_spend_entries",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.VENDOR_UPDATE: {
        "handler": "app.domains.business.activity.handlers.business_operations.vendor_update",
        "permission": "can_add_operations_records",
        "typed_table": "operations_vendor_updates",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.OPS_APPROVAL_REQUEST: {
        "handler": "app.domains.business.activity.handlers.business_operations.approval_request",
        "permission": None,
        "typed_table": "operations_approval_requests",
        "affected_slices": ("pulse", "moments"),
        "editable": False,
        "deletable": False,
    },
    ActionType.ISSUE_RISK: {
        "handler": "app.domains.business.activity.handlers.business_operations.issue_risk",
        "permission": "can_add_operations_records",
        "typed_table": "operations_issues",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
    ActionType.OPERATIONAL_IMPROVEMENT: {
        "handler": "app.domains.business.activity.handlers.business_operations.operational_improvement",
        "permission": "can_add_operations_records",
        "typed_table": "operations_improvements",
        "affected_slices": ("pulse", "moments"),
        "editable": True,
        "deletable": True,
    },
}

ACTION_REGISTRY: MappingProxyType[ActionType, dict] = MappingProxyType(_REGISTRY)
