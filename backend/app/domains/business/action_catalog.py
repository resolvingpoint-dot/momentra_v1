"""Business Action Center catalog — single source for hub tiles + renderer metadata.

Returned by GET /business/active/{moment_id}/action-catalog (and enriching quick-add).
Clients must not hardcode action lists.
"""
from __future__ import annotations

from typing import Any

from app.domains.business.activity.types import ActionType

# renderer_id → ProgressiveActionForm field schema keys (honest/min fields for Run 7)
_FIELD = dict[str, Any]


def _text(key: str, label: str, *, required: bool = True, multiline: bool = False) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "textarea" if multiline else "text",
        "required": required,
    }


def _amount(key: str = "amount_minor", label: str = "Amount") -> _FIELD:
    return {"key": key, "label": label, "field_type": "amount", "required": True}


def _date(key: str, label: str, *, required: bool = False) -> _FIELD:
    return {"key": key, "label": label, "field_type": "date", "required": required}


def _select(key: str, label: str, options: list[dict[str, str]], *, required: bool = True) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "single_select",
        "required": required,
        "options": options,
    }


def _member(key: str, label: str, *, required: bool = False) -> _FIELD:
    return {"key": key, "label": label, "field_type": "member_picker", "required": required}


# --------------------------------------------------------------------------- #
# Catalog entries: action_type → hub + renderer metadata
# --------------------------------------------------------------------------- #

TEAM_OPERATIONS_CATALOG: list[dict[str, Any]] = [
    {
        "action_type": ActionType.TEAM_UPDATE.value,
        "action_id": "team_update",
        "label": "Team Update",
        "icon": "task_alt",
        "category_id": "core",
        "category_label": "Core",
        "renderer_id": "team_ops.team_update",
        "cta_label": "Save update",
        "display_order": 10,
        "fields": [
            _text("title", "Title"),
            _text("description", "Details", required=False, multiline=True),
            _select(
                "priority",
                "Priority",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                ],
                required=False,
            ),
            _amount(),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.RECOGNITION.value,
        "action_id": "recognition",
        "label": "Recognition",
        "icon": "star",
        "category_id": "people",
        "category_label": "People",
        "renderer_id": "team_ops.recognition",
        "cta_label": "Give recognition",
        "display_order": 20,
        "fields": [
            _text("title", "Recognition"),
            _member("recipient_member_id", "Recipient", required=True),
            _text("notes", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["title", "recipient_member_id"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.MEETING.value,
        "action_id": "meeting",
        "label": "Meeting",
        "icon": "calendar_today",
        "category_id": "core",
        "category_label": "Core",
        "renderer_id": "team_ops.meeting",
        "cta_label": "Save meeting",
        "display_order": 30,
        "fields": [
            _text("title", "Meeting title"),
            _date("meeting_at", "When", required=False),
            _text("notes", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.ISSUE.value,
        "action_id": "issue",
        "label": "Issue",
        "icon": "warning",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "team_ops.issue",
        "cta_label": "Log issue",
        "display_order": 40,
        "fields": [
            _text("title", "Issue title"),
            _select(
                "severity",
                "Severity",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"},
                ],
            ),
            _text("description", "Description", required=False, multiline=True),
        ],
        "required_fields": ["title", "severity"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.APPROVAL_REQUEST.value,
        "action_id": "approval",
        "label": "Approval",
        "icon": "check_circle",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "team_ops.approval",
        "cta_label": "Request approval",
        "display_order": 50,
        "fields": [
            _text("title", "Request title"),
            _amount(),
            _text("reason", "Reason", multiline=True),
            _member("approver_id", "Approver", required=True),
        ],
        "required_fields": ["title", "amount_minor", "reason", "approver_id"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.REVIEW.value,
        "action_id": "review",
        "label": "Review",
        "icon": "rate_review",
        "category_id": "core",
        "category_label": "Core",
        "renderer_id": "team_ops.review",
        "cta_label": "Save review",
        "display_order": 60,
        "fields": [
            _text("title", "Review title"),
            _text("notes", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.ESCALATION.value,
        "action_id": "escalation",
        "label": "Escalation",
        "icon": "priority_high",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "team_ops.escalation",
        "cta_label": "Escalate",
        "display_order": 70,
        "fields": [
            _text("title", "Escalation"),
            _select(
                "severity",
                "Severity",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"},
                ],
            ),
            _text("notes", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["title", "severity"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.PARTICIPATION.value,
        "action_id": "participation",
        "label": "Participation",
        "icon": "groups",
        "category_id": "people",
        "category_label": "People",
        "renderer_id": "team_ops.participation",
        "cta_label": "Save",
        "display_order": 80,
        "fields": [
            _text("title", "Title"),
            _member("member_id", "Member", required=False),
            _text("notes", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.MEMBER_UPDATE.value,
        "action_id": "member_update",
        "label": "Member Update",
        "icon": "person",
        "category_id": "people",
        "category_label": "People",
        "renderer_id": "team_ops.member_update",
        "cta_label": "Save update",
        "display_order": 90,
        "fields": [
            _text("title", "Update"),
            _member("member_id", "Member", required=False),
            _text("notes", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.NOTE.value,
        "action_id": "note",
        "label": "Note",
        "icon": "edit_note",
        "category_id": "core",
        "category_label": "Core",
        "renderer_id": "team_ops.note",
        "cta_label": "Save note",
        "display_order": 100,
        "fields": [
            _text("title", "Title"),
            _text("notes", "Note", multiline=True),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
]

RUNWAY_CATALOG: list[dict[str, Any]] = [
    {
        "action_type": ActionType.CASH_INFLOW.value,
        "action_id": "cash_inflow",
        "label": "Cash Inflow",
        "icon": "payments",
        "category_id": "finance",
        "category_label": "Finance",
        "renderer_id": "runway.cash_inflow",
        "cta_label": "Record inflow",
        "display_order": 10,
        "fields": [
            _text("title", "Label", required=False),
            _amount(),
            _select(
                "inflow_type",
                "Type",
                [
                    {"value": "revenue_collected", "label": "Revenue"},
                    {"value": "investor_funding", "label": "Investor funding"},
                    {"value": "owner_contribution", "label": "Owner contribution"},
                    {"value": "bank_loan", "label": "Loan"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _date("inflow_date", "Date", required=True),
            _text("description", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["amount_minor", "inflow_type", "inflow_date"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.EXPENSE_BURN.value,
        "action_id": "expense_burn",
        "label": "Burn Expense",
        "icon": "local_fire_department",
        "category_id": "finance",
        "category_label": "Finance",
        "renderer_id": "runway.expense_burn",
        "cta_label": "Record burn",
        "display_order": 20,
        "fields": [
            _amount(),
            _select(
                "expense_category",
                "Category",
                [
                    {"value": "salaries", "label": "Salaries"},
                    {"value": "marketing", "label": "Marketing"},
                    {"value": "technology", "label": "Technology"},
                    {"value": "operations", "label": "Operations"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _date("expense_date", "Date", required=True),
            _text("description", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["amount_minor", "expense_category", "expense_date"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.RUNWAY_RISK.value,
        "action_id": "runway_risk",
        "label": "Runway Risk",
        "icon": "warning",
        "category_id": "risk",
        "category_label": "Risk",
        "renderer_id": "runway.runway_risk",
        "cta_label": "Log risk",
        "display_order": 30,
        "fields": [
            _text("title", "Risk title"),
            _select(
                "severity",
                "Severity",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"},
                ],
            ),
            _text("description", "Description", required=False, multiline=True),
        ],
        "required_fields": ["title", "severity"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.FINANCIAL_UPDATE.value,
        "action_id": "financial_update",
        "label": "Financial Update",
        "icon": "edit_note",
        "category_id": "finance",
        "category_label": "Finance",
        "renderer_id": "runway.financial_update",
        "cta_label": "Save update",
        "display_order": 40,
        "fields": [
            _select(
                "update_type",
                "Update type",
                [
                    {"value": "cash_available", "label": "Cash available"},
                    {"value": "monthly_burn", "label": "Monthly burn"},
                    {"value": "revenue_estimate", "label": "Revenue estimate"},
                    {"value": "runway_threshold", "label": "Runway threshold"},
                ],
            ),
            _text("reason", "Reason", multiline=True),
            _amount("amount_minor", "New value (minor)"),
        ],
        "required_fields": ["update_type", "reason", "amount_minor"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.STRATEGIC_DECISION.value,
        "action_id": "strategic_decision",
        "label": "Strategic Decision",
        "icon": "lightbulb",
        "category_id": "strategy",
        "category_label": "Strategy",
        "renderer_id": "runway.strategic_decision",
        "cta_label": "Save decision",
        "display_order": 50,
        "fields": [
            _text("title", "Decision"),
            _select(
                "decision_type",
                "Type",
                [
                    {"value": "hiring", "label": "Hiring"},
                    {"value": "expansion", "label": "Expansion"},
                    {"value": "funding", "label": "Funding"},
                    {"value": "cost_reduction", "label": "Cost reduction"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _text("description", "Details", required=False, multiline=True),
        ],
        "required_fields": ["title", "decision_type"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
]

OPERATIONS_CATALOG: list[dict[str, Any]] = [
    {
        "action_type": ActionType.SPEND_ENTRY.value,
        "action_id": "spend_entry",
        "label": "Spend Entry",
        "icon": "shopping_cart",
        "category_id": "spend",
        "category_label": "Spend",
        "renderer_id": "ops.spend_entry",
        "cta_label": "Save spend",
        "display_order": 10,
        "fields": [
            _text("title", "Spend name"),
            _amount(),
            _select(
                "spend_category",
                "Category",
                [
                    {"value": "purchase", "label": "Purchase"},
                    {"value": "vendor_payment", "label": "Vendor payment"},
                    {"value": "staff_cost", "label": "Staff cost"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _date("spend_date", "Date", required=True),
            _text("vendor_name", "Vendor", required=False),
        ],
        "required_fields": ["title", "amount_minor", "spend_category", "spend_date"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.VENDOR_UPDATE.value,
        "action_id": "vendor_update",
        "label": "Vendor Update",
        "icon": "storefront",
        "category_id": "vendor",
        "category_label": "Vendors",
        "renderer_id": "ops.vendor_update",
        "cta_label": "Save vendor update",
        "display_order": 20,
        "fields": [
            _text("vendor_name", "Vendor name"),
            _select(
                "vendor_event_type",
                "Event",
                [
                    {"value": "new_vendor", "label": "New vendor"},
                    {"value": "vendor_issue", "label": "Issue"},
                    {"value": "contract_renewal", "label": "Renewal"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _text("description", "Notes", required=False, multiline=True),
        ],
        "required_fields": ["vendor_name", "vendor_event_type"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.OPS_APPROVAL_REQUEST.value,
        "action_id": "ops_approval",
        "label": "Approval",
        "icon": "check_circle",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "ops.approval",
        "cta_label": "Request approval",
        "display_order": 30,
        "fields": [
            _text("title", "Request title"),
            _amount(),
            _text("description", "Description", multiline=True),
        ],
        "required_fields": ["title", "description"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.ISSUE_RISK.value,
        "action_id": "ops_issue",
        "label": "Issue",
        "icon": "report_problem",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "ops.issue",
        "cta_label": "Log issue",
        "display_order": 40,
        "fields": [
            _text("title", "Issue title"),
            _select(
                "severity",
                "Severity",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"},
                ],
            ),
            _text("description", "Description", required=False, multiline=True),
        ],
        "required_fields": ["title", "severity"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.OPERATIONAL_IMPROVEMENT.value,
        "action_id": "operational_improvement",
        "label": "Operational Improvement",
        "icon": "trending_up",
        "category_id": "improvement",
        "category_label": "Improvement",
        "renderer_id": "ops.operational_improvement",
        "cta_label": "Save improvement",
        "display_order": 50,
        "fields": [
            _text("title", "Improvement"),
            _select(
                "improvement_type",
                "Type",
                [
                    {"value": "process_improvement", "label": "Process"},
                    {"value": "budget_control_improvement", "label": "Budget control"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _text("description", "Details", required=False, multiline=True),
        ],
        "required_fields": ["title", "improvement_type"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
]

_BY_MOMENT_TYPE: dict[str, list[dict[str, Any]]] = {
    "TEAM_OPERATIONS": TEAM_OPERATIONS_CATALOG,
    "team_operations": TEAM_OPERATIONS_CATALOG,
    "BUSINESS_RUNWAY": RUNWAY_CATALOG,
    "business_runway": RUNWAY_CATALOG,
    "BUSINESS_OPERATIONS": OPERATIONS_CATALOG,
    "business_operations": OPERATIONS_CATALOG,
}


def catalog_for_moment_type(moment_type: str) -> list[dict[str, Any]]:
    return list(_BY_MOMENT_TYPE.get(moment_type) or _BY_MOMENT_TYPE.get(moment_type.upper()) or [])


def get_action_entry(moment_type: str, action_type_or_id: str) -> dict[str, Any] | None:
    key = (action_type_or_id or "").strip()
    for entry in catalog_for_moment_type(moment_type):
        if entry["action_type"] == key or entry["action_id"] == key or entry["renderer_id"] == key:
            return entry
    return None


def build_action_catalog_payload(
    *,
    moment_id: str,
    moment_type: str,
    members: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Hub + categories for Action Center (backend-owned catalog)."""
    actions = catalog_for_moment_type(moment_type)
    categories: dict[str, dict[str, Any]] = {}
    for a in sorted(actions, key=lambda x: x["display_order"]):
        cid = a["category_id"]
        if cid not in categories:
            categories[cid] = {
                "id": cid,
                "label": a["category_label"],
                "actions": [],
            }
        categories[cid]["actions"].append(
            {
                "action_id": a["action_id"],
                "action_type": a["action_type"],
                "label": a["label"],
                "icon": a["icon"],
                "renderer_id": a["renderer_id"],
                "cta_label": a["cta_label"],
                "display_order": a["display_order"],
                "supports": a.get("supports") or {},
            }
        )
    return {
        "moment_id": moment_id,
        "moment_type": moment_type.upper() if moment_type else moment_type,
        "template_id": _template_id(moment_type),
        "categories": list(categories.values()),
        "actions": [
            {
                "action_id": a["action_id"],
                "action_type": a["action_type"],
                "label": a["label"],
                "icon": a["icon"],
                "renderer_id": a["renderer_id"],
                "category_id": a["category_id"],
                "cta_label": a["cta_label"],
                "display_order": a["display_order"],
                "supports": a.get("supports") or {},
            }
            for a in sorted(actions, key=lambda x: x["display_order"])
        ],
        "members": members or [],
    }


def build_renderer_metadata(
    moment_type: str, action_type_or_id: str, *, moment_id: str | None = None
) -> dict[str, Any] | None:
    entry = get_action_entry(moment_type, action_type_or_id)
    if entry is None:
        return None
    return {
        "moment_id": moment_id,
        "moment_type": moment_type.upper() if moment_type else moment_type,
        "action_id": entry["action_id"],
        "action_type": entry["action_type"],
        "label": entry["label"],
        "renderer_id": entry["renderer_id"],
        "cta_label": entry["cta_label"],
        "fields": entry["fields"],
        "required_fields": entry["required_fields"],
        "supports": entry.get("supports") or {},
        "validation": {"required_fields": entry["required_fields"]},
    }


def _template_id(moment_type: str) -> str:
    mt = (moment_type or "").upper()
    if mt == "TEAM_OPERATIONS":
        return "business.team_ops"
    if mt == "BUSINESS_RUNWAY":
        return "business.runway"
    if mt == "BUSINESS_OPERATIONS":
        return "business.operations"
    return f"business.{mt.lower()}"
