"""Business Action Center catalog — single source for hub tiles + renderer metadata.

Returned by GET /business/active/{moment_id}/action-catalog (and enriching quick-add).
Clients must not hardcode action lists. Field types drive native controls on every client.
"""
from __future__ import annotations

from typing import Any

from app.domains.business.activity.types import ActionType

_FIELD = dict[str, Any]

# Bump when catalog field shapes change so clients invalidate schema caches.
ACTION_CATALOG_SCHEMA_VERSION = 3


def _text(key: str, label: str, *, required: bool = True, multiline: bool = False) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "textarea" if multiline else "text",
        "required": required,
    }


def _amount(key: str = "amount_minor", label: str = "Amount", *, required: bool = True) -> _FIELD:
    return {"key": key, "label": label, "field_type": "amount", "required": required}


def _date(key: str, label: str, *, required: bool = False) -> _FIELD:
    return {"key": key, "label": label, "field_type": "date", "required": required}


def _datetime(key: str, label: str, *, required: bool = False) -> _FIELD:
    """Date + time field — use when time-of-day matters (e.g. meeting_at)."""
    return {"key": key, "label": label, "field_type": "datetime", "required": required}


def _searchable(
    key: str, label: str, options: list[dict[str, str]], *, required: bool = True
) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "searchable_select",
        "required": required,
        "options": options,
        "searchable": True,
    }


def _segmented(
    key: str, label: str, options: list[dict[str, str]], *, required: bool = True
) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "segmented",
        "required": required,
        "options": options,
    }


def _select(key: str, label: str, options: list[dict[str, str]], *, required: bool = True) -> _FIELD:
    """Legacy alias — prefer _searchable or _segmented."""
    if len(options) <= 4:
        return _segmented(key, label, options, required=required)
    return _searchable(key, label, options, required=required)


def _member(key: str, label: str, *, required: bool = False) -> _FIELD:
    return {"key": key, "label": label, "field_type": "member_picker", "required": required}


def _members(key: str, label: str, *, required: bool = False) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "member_multi_select",
        "required": required,
    }


def _vendor_picker(key: str, label: str, *, required: bool = False) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "vendor_picker",
        "required": required,
        "allow_custom": True,
    }


def _chips(key: str, label: str, options: list[dict[str, str]], *, required: bool = True) -> _FIELD:
    """Deprecated — maps to segmented for ≤4 options, searchable otherwise."""
    return _select(key, label, options, required=required)


def _toggle(key: str, label: str, *, default: bool = False) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "toggle",
        "required": False,
        "default": default,
    }


def _attachment(key: str = "attachment_paths", label: str = "Attachment", *, required: bool = False) -> _FIELD:
    return {
        "key": key,
        "label": label,
        "field_type": "attachment",
        "required": required,
        "multiple": True,
    }


def _amount_when(
    key: str,
    label: str,
    *,
    when_field: str,
    when_equals: str,
    label_override: str | None = None,
) -> _FIELD:
    field = _amount(key, label_override or label)
    field["visible_when"] = {"field": when_field, "equals": when_equals}
    if label_override:
        field["label"] = label_override
    return field


# --------------------------------------------------------------------------- #
# Catalog entries
# --------------------------------------------------------------------------- #

TEAM_OPERATIONS_CATALOG: list[dict[str, Any]] = [
    {
        "action_type": ActionType.TEAM_UPDATE.value,
        "action_id": "team_update",
        "label": "Team Update",
        "icon": "task_alt",
        "category_id": "core",
        "category_label": "Core",
        "renderer_id": "schema.generic",
        "cta_label": "Save update",
        "display_order": 10,
        "fields": [
            _text("title", "Title"),
            _text("description", "Details", required=False, multiline=True),
            _segmented(
                "priority",
                "Priority",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                ],
                required=False,
            ),
            _amount(required=False),
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
        "renderer_id": "schema.generic",
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
        "renderer_id": "schema.generic",
        "cta_label": "Save meeting",
        "display_order": 30,
        "fields": [
            _text("title", "Meeting title"),
            _datetime("meeting_at", "When", required=False),
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
        "renderer_id": "schema.generic",
        "cta_label": "Log issue",
        "display_order": 40,
        "fields": [
            _text("title", "Issue title"),
            _segmented(
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
        "renderer_id": "schema.generic",
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
        "renderer_id": "schema.generic",
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
        "renderer_id": "schema.generic",
        "cta_label": "Escalate",
        "display_order": 70,
        "fields": [
            _text("title", "Escalation"),
            _segmented(
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
        "renderer_id": "schema.generic",
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
        "renderer_id": "schema.generic",
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
        "renderer_id": "schema.generic",
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
        "renderer_id": "schema.generic",
        "cta_label": "Record inflow",
        "display_order": 10,
        "notify_defaults": {"post_to_activity": True, "notify_finance_admins": False},
        "fields": [
            _text("title", "Source"),
            _amount(),
            _searchable(
                "inflow_type",
                "Inflow type",
                [
                    {"value": "revenue_collected", "label": "Revenue"},
                    {"value": "investor_funding", "label": "Investor funding"},
                    {"value": "owner_contribution", "label": "Owner contribution"},
                    {"value": "bank_loan", "label": "Loan"},
                    {"value": "government_grant", "label": "Grant"},
                    {"value": "refund", "label": "Refund"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _date("inflow_date", "Received date", required=True),
            _text("reference", "Reference", required=False),
            _text("description", "Notes", required=False, multiline=True),
            _attachment(),
            _toggle("share_update", "Share update", default=True),
            _toggle("notify_finance_admins", "Notify finance admins", default=False),
        ],
        "required_fields": ["title", "amount_minor", "inflow_type", "inflow_date"],
        "supports": {
            "drafts": True,
            "favorites": True,
            "review": True,
            "attachments": True,
        },
    },
    {
        "action_type": ActionType.EXPENSE_BURN.value,
        "action_id": "expense_burn",
        "label": "Burn Expense",
        "icon": "local_fire_department",
        "category_id": "finance",
        "category_label": "Finance",
        "renderer_id": "schema.generic",
        "cta_label": "Record burn",
        "display_order": 20,
        "notify_defaults": {"post_to_activity": True, "notify_on_threshold": True},
        "fields": [
            _amount(),
            _searchable(
                "expense_category",
                "Expense category",
                [
                    {"value": "salaries", "label": "Salaries"},
                    {"value": "rent", "label": "Rent"},
                    {"value": "marketing", "label": "Marketing"},
                    {"value": "technology", "label": "Technology"},
                    {"value": "operations", "label": "Operations"},
                    {"value": "legal", "label": "Legal"},
                    {"value": "travel", "label": "Travel"},
                    {"value": "insurance", "label": "Insurance"},
                    {"value": "taxes", "label": "Taxes"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _date("expense_date", "Date", required=True),
            _text("description", "Notes", required=False, multiline=True),
            _attachment(),
            _toggle("notify_finance_owner", "Notify finance owner if over threshold", default=True),
        ],
        "required_fields": ["amount_minor", "expense_category", "expense_date"],
        "supports": {
            "drafts": True,
            "favorites": True,
            "review": True,
            "attachments": True,
        },
    },
    {
        "action_type": ActionType.RUNWAY_RISK.value,
        "action_id": "runway_risk",
        "label": "Runway Risk",
        "icon": "warning",
        "category_id": "risk",
        "category_label": "Risk",
        "renderer_id": "schema.generic",
        "cta_label": "Log risk",
        "display_order": 30,
        "notify_defaults": {
            "post_to_activity": True,
            "notify_owner": True,
            "critical_admins_push": True,
            "action_center": True,
        },
        "fields": [
            _text("title", "Risk title"),
            _segmented(
                "severity",
                "Severity",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"},
                ],
            ),
            _searchable(
                "expected_impact",
                "Impact",
                [
                    {"value": "lt_1_month", "label": "Less than 1 month"},
                    {"value": "1_3_months", "label": "1–3 months"},
                    {"value": "3_6_months", "label": "3–6 months"},
                    {"value": "6_plus_months", "label": "6+ months"},
                ],
                required=False,
            ),
            _member("owner_id", "Owner", required=False),
            _date("target_resolution_date", "Due date", required=False),
            _text("description", "Description", required=False, multiline=True),
            _toggle("notify_owner", "Notify owner", default=True),
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
        "renderer_id": "schema.generic",
        "cta_label": "Save update",
        "display_order": 40,
        "notify_defaults": {"post_to_activity": True, "notify_on_significant": True},
        "fields": [
            _searchable(
                "update_type",
                "Update type",
                [
                    {"value": "cash_available", "label": "Cash available"},
                    {"value": "monthly_burn", "label": "Monthly burn"},
                    {"value": "revenue_estimate", "label": "Revenue estimate"},
                    {"value": "runway_threshold", "label": "Runway threshold"},
                ],
            ),
            {
                "key": "amount_minor",
                "label": "New value",
                "field_type": "amount",
                "required": True,
                "label_when": [
                    {"field": "update_type", "equals": "cash_available", "label": "New cash available"},
                    {"field": "update_type", "equals": "monthly_burn", "label": "New monthly burn"},
                    {
                        "field": "update_type",
                        "equals": "revenue_estimate",
                        "label": "New revenue estimate",
                    },
                    {
                        "field": "update_type",
                        "equals": "runway_threshold",
                        "label": "New runway threshold",
                    },
                ],
            },
            _date("effective_date", "Effective date", required=False),
            _text("reason", "Reason", multiline=True),
            _toggle("share_update", "Share update", default=True),
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
        "renderer_id": "schema.generic",
        "cta_label": "Save decision",
        "display_order": 50,
        "notify_defaults": {"post_to_activity": True, "notify_leadership": True},
        "fields": [
            _text("title", "Decision title"),
            _searchable(
                "decision_type",
                "Decision category",
                [
                    {"value": "hiring", "label": "Hiring"},
                    {"value": "expansion", "label": "Expansion"},
                    {"value": "funding", "label": "Funding"},
                    {"value": "cost_reduction", "label": "Cost reduction"},
                    {"value": "pricing", "label": "Pricing"},
                    {"value": "operations", "label": "Operations"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _member("decision_owner_id", "Owner", required=False),
            _date("target_completion_date", "Target completion", required=False),
            _searchable(
                "expected_impact",
                "Expected impact",
                [
                    {"value": "increase_runway", "label": "Increase runway"},
                    {"value": "reduce_runway", "label": "Reduce runway"},
                    {"value": "neutral", "label": "Neutral"},
                    {"value": "unknown", "label": "Unknown"},
                ],
                required=False,
            ),
            _text("description", "Details", required=False, multiline=True),
            _toggle("notify_leadership", "Notify leadership", default=True),
            _members("notify_approver_ids", "Notify approvers", required=False),
        ],
        "required_fields": ["title", "decision_type"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
]

OPERATIONS_CATALOG: list[dict[str, Any]] = [
    {
        "action_type": ActionType.SPEND_ENTRY.value,
        "action_id": "spend_entry",
        "label": "Spend entry",
        "subtitle": "Record a purchase, payment, or staff cost",
        "icon": "shopping_cart",
        "category_id": "spend",
        "category_label": "Spend",
        "renderer_id": "schema.generic",
        "cta_label": "Save spend",
        "display_order": 10,
        "notify_defaults": {"post_to_activity": True, "notify_managers": False},
        "fields": [
            _text("title", "What was this spend for?"),
            _amount(),
            _searchable(
                "spend_category",
                "Category",
                [
                    {"value": "purchase", "label": "Purchase"},
                    {"value": "vendor_payment", "label": "Vendor payment"},
                    {"value": "staff_cost", "label": "Staff cost"},
                    {"value": "utility_bill", "label": "Utilities"},
                    {"value": "travel_expense", "label": "Travel"},
                    {"value": "rent", "label": "Rent"},
                    {"value": "marketing_spend", "label": "Marketing"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _vendor_picker("vendor_name", "Paid to / Vendor", required=False),
            {
                **_segmented(
                    "payment_method",
                    "Payment method",
                    [
                        {"value": "cash", "label": "Cash"},
                        {"value": "upi", "label": "Online"},
                    ],
                ),
                "default": "cash",
            },
            {
                **_segmented(
                    "payment_status",
                    "Payment",
                    [
                        {"value": "paid_full", "label": "Paid completely"},
                        {"value": "paid_partial", "label": "Partially paid"},
                        {"value": "unpaid", "label": "Complete credit"},
                    ],
                ),
                "default": "paid_full",
            },
            _amount_when(
                "amount_paid_minor",
                "Amount paid",
                when_field="payment_status",
                when_equals="paid_partial",
            ),
            _date("spend_date", "Date", required=True),
            _text("description", "Notes", required=False, multiline=True),
            _attachment(),
            _toggle("notify_managers", "Notify managers", default=False),
        ],
        "required_fields": ["title", "amount_minor", "spend_category", "spend_date"],
        "supports": {
            "drafts": True,
            "favorites": True,
            "review": True,
            "attachments": True,
        },
    },
    {
        "action_type": ActionType.VENDOR_UPDATE.value,
        "action_id": "vendor_update",
        "label": "Vendor update",
        "subtitle": "Log a new vendor, issue, renewal, or change",
        "icon": "storefront",
        "category_id": "vendor",
        "category_label": "Vendors",
        "renderer_id": "schema.generic",
        "cta_label": "Save vendor update",
        "display_order": 20,
        "notify_defaults": {"post_to_activity": True, "notify_managers": False},
        "fields": [
            _vendor_picker("vendor_name", "Vendor", required=True),
            _searchable(
                "vendor_event_type",
                "Update type",
                [
                    {"value": "new_vendor", "label": "New vendor"},
                    {"value": "vendor_issue", "label": "Issue"},
                    {"value": "contract_renewal", "label": "Renewal"},
                    {"value": "contract_change", "label": "Contract update"},
                    {"value": "payment_status", "label": "Payment update"},
                    {"value": "contact_update", "label": "Contact update"},
                    {"value": "vendor_suspension", "label": "Vendor closed"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _segmented(
                "vendor_status",
                "Status",
                [
                    {"value": "active", "label": "Open"},
                    {"value": "under_review", "label": "In progress"},
                    {"value": "terminated", "label": "Resolved"},
                ],
                required=False,
            ),
            _date("effective_date", "Effective date", required=False),
            _text("description", "Notes", required=False, multiline=True),
            _toggle("notify_managers", "Notify managers", default=False),
        ],
        "required_fields": ["vendor_name", "vendor_event_type"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.OPERATIONAL_IMPROVEMENT.value,
        "action_id": "operational_improvement",
        "label": "Operational improvement",
        "subtitle": "Capture a process or budget-control improvement",
        "icon": "trending_up",
        "category_id": "improvement",
        "category_label": "Improvement",
        "renderer_id": "schema.generic",
        "cta_label": "Save improvement",
        "display_order": 30,
        "notify_defaults": {"post_to_activity": True, "notify_managers": False},
        "fields": [
            _text("title", "Improvement title"),
            _searchable(
                "improvement_type",
                "Area",
                [
                    {"value": "process_improvement", "label": "Process"},
                    {"value": "budget_control_improvement", "label": "Budget control"},
                    {"value": "inventory_improvement", "label": "Inventory"},
                    {"value": "vendor_experience_improvement", "label": "Vendor management"},
                    {"value": "staffing_scheduling_improvement", "label": "Staff"},
                    {"value": "compliance_improvement", "label": "Compliance"},
                    {"value": "service_quality_improvement", "label": "Customer service"},
                    {"value": "operational_control_improvement", "label": "Technology"},
                    {"value": "approval_flow_improvement", "label": "Approvals"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _segmented(
                "priority",
                "Priority",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                ],
                required=False,
            ),
            _searchable(
                "expected_impact",
                "Expected impact",
                [
                    {"value": "improve_speed", "label": "Save time"},
                    {"value": "reduce_cost", "label": "Reduce cost"},
                    {"value": "improve_service", "label": "Improve quality"},
                    {"value": "reduce_issues", "label": "Reduce risk"},
                    {"value": "improve_control", "label": "Improve control"},
                    {"value": "improve_visibility", "label": "Improve visibility"},
                ],
                required=False,
            ),
            _member("owner_id", "Owner", required=False),
            _date("target_date", "Target date", required=False),
            _text("description", "Details", required=False, multiline=True),
        ],
        "required_fields": ["title", "improvement_type"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.OPS_APPROVAL_REQUEST.value,
        "action_id": "ops_approval",
        "label": "Approval request",
        "subtitle": "Request approval from workspace members",
        "icon": "check_circle",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "schema.generic",
        "cta_label": "Send approval request",
        "display_order": 40,
        "notify_defaults": {"post_to_activity": True, "notify_approvers": True},
        "fields": [
            _text("title", "Request title"),
            _searchable(
                "request_type",
                "Approval type",
                [
                    {"value": "purchase", "label": "Purchase"},
                    {"value": "vendor_approval", "label": "Vendor payment"},
                    {"value": "expense_approval", "label": "Expense"},
                    {"value": "budget_change", "label": "Budget change"},
                    {"value": "hiring", "label": "Hiring"},
                    {"value": "operational_request", "label": "Operational change"},
                    {"value": "contract", "label": "Contract"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            _amount(required=False),
            _members("approver_ids", "Requested from", required=True),
            _date("due_date", "Due date", required=False),
            _segmented(
                "priority",
                "Priority",
                [
                    {"value": "medium", "label": "Normal"},
                    {"value": "high", "label": "Urgent"},
                ],
                required=False,
            ),
            _text("description", "Description", required=False, multiline=True),
        ],
        "required_fields": ["title", "request_type", "approver_ids"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.ISSUE_RISK.value,
        "action_id": "ops_issue",
        "label": "Issue",
        "subtitle": "Log an operational issue or risk",
        "icon": "report_problem",
        "category_id": "governance",
        "category_label": "Governance",
        "renderer_id": "schema.generic",
        "cta_label": "Log issue",
        "display_order": 50,
        "notify_defaults": {"post_to_activity": True, "notify_managers": False},
        "fields": [
            _text("title", "Issue title"),
            _segmented(
                "severity",
                "Severity",
                [
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"},
                ],
            ),
            _member("owner_id", "Owner", required=False),
            _date("target_resolution_date", "Target date", required=False),
            _text("description", "Description", required=False, multiline=True),
        ],
        "required_fields": ["title", "severity"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
    {
        "action_type": ActionType.OPS_GENERAL_UPDATE.value,
        "action_id": "ops_general_update",
        "label": "General update",
        "subtitle": "Post a note to the operations activity",
        "icon": "notes",
        "category_id": "updates",
        "category_label": "Updates",
        "renderer_id": "schema.generic",
        "cta_label": "Post update",
        "display_order": 60,
        "notify_defaults": {"post_to_activity": True, "notify_managers": False},
        "fields": [
            _text("title", "Update title"),
            _text("description", "Notes", required=False, multiline=True),
            _toggle("notify_managers", "Notify managers", default=False),
            _members("notify_user_ids", "Notify members", required=False),
        ],
        "required_fields": ["title"],
        "supports": {"drafts": True, "favorites": True, "review": True},
    },
]

# Future moment stubs — hub shows coming-soon tiles; no live actions yet.
_COMING_SOON_STUB: list[dict[str, Any]] = []

FUTURE_MOMENT_STUBS: dict[str, dict[str, Any]] = {
    "CASHFLOW": {
        "coming_soon": True,
        "label": "Cashflow",
        "subtitle": "Cash position and forecasts — coming soon",
        "actions": _COMING_SOON_STUB,
    },
    "HR": {
        "coming_soon": True,
        "label": "HR",
        "subtitle": "People and payroll actions — coming soon",
        "actions": _COMING_SOON_STUB,
    },
    "INVENTORY": {
        "coming_soon": True,
        "label": "Inventory",
        "subtitle": "Stock and fulfillment — coming soon",
        "actions": _COMING_SOON_STUB,
    },
    "CRM": {
        "coming_soon": True,
        "label": "CRM",
        "subtitle": "Pipeline and customer actions — coming soon",
        "actions": _COMING_SOON_STUB,
    },
    "PROJECT_OPERATIONS": {
        "coming_soon": True,
        "label": "Projects",
        "subtitle": "Project operations — coming soon",
        "actions": _COMING_SOON_STUB,
    },
}

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


def future_stub_for_moment_type(moment_type: str) -> dict[str, Any] | None:
    mt = (moment_type or "").upper()
    stub = FUTURE_MOMENT_STUBS.get(mt)
    if stub:
        return stub
    # Also allow lowercase workspace module keys
    for key, val in FUTURE_MOMENT_STUBS.items():
        if key.lower() == (moment_type or "").lower():
            return val
    return None


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
    vendors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Hub + categories for Action Center (backend-owned catalog)."""
    stub = future_stub_for_moment_type(moment_type)
    if stub and not catalog_for_moment_type(moment_type):
        return {
            "moment_id": moment_id,
            "moment_type": moment_type.upper() if moment_type else moment_type,
            "template_id": _template_id(moment_type),
            "schema_version": ACTION_CATALOG_SCHEMA_VERSION,
            "coming_soon": True,
            "coming_soon_label": stub.get("label"),
            "coming_soon_subtitle": stub.get("subtitle"),
            "categories": [],
            "actions": [],
            "members": members or [],
            "vendors": vendors or [],
            "future_modules": [
                {
                    "id": k.lower(),
                    "label": v["label"],
                    "subtitle": v["subtitle"],
                    "coming_soon": True,
                }
                for k, v in FUTURE_MOMENT_STUBS.items()
            ],
        }

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
                "subtitle": a.get("subtitle"),
                "icon": a["icon"],
                "renderer_id": a["renderer_id"],
                "cta_label": a["cta_label"],
                "display_order": a["display_order"],
                "supports": a.get("supports") or {},
                "notify_defaults": a.get("notify_defaults") or {},
            }
        )
    return {
        "moment_id": moment_id,
        "moment_type": moment_type.upper() if moment_type else moment_type,
        "template_id": _template_id(moment_type),
        "schema_version": ACTION_CATALOG_SCHEMA_VERSION,
        "coming_soon": False,
        "categories": list(categories.values()),
        "actions": [
            {
                "action_id": a["action_id"],
                "action_type": a["action_type"],
                "label": a["label"],
                "subtitle": a.get("subtitle"),
                "icon": a["icon"],
                "renderer_id": a["renderer_id"],
                "category_id": a["category_id"],
                "cta_label": a["cta_label"],
                "display_order": a["display_order"],
                "supports": a.get("supports") or {},
                "notify_defaults": a.get("notify_defaults") or {},
                "fields": a.get("fields") or [],
                "required_fields": a.get("required_fields") or [],
            }
            for a in sorted(actions, key=lambda x: x["display_order"])
        ],
        "members": members or [],
        "vendors": vendors or [],
        "future_modules": [
            {
                "id": k.lower(),
                "label": v["label"],
                "subtitle": v["subtitle"],
                "coming_soon": True,
            }
            for k, v in FUTURE_MOMENT_STUBS.items()
        ],
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
        "subtitle": entry.get("subtitle"),
        "renderer_id": entry["renderer_id"],
        "cta_label": entry["cta_label"],
        "fields": entry["fields"],
        "required_fields": entry["required_fields"],
        "supports": entry.get("supports") or {},
        "notify_defaults": entry.get("notify_defaults") or {},
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
