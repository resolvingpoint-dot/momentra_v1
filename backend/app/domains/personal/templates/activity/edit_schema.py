"""Build edit_schema payloads for template activity detail responses."""
from __future__ import annotations

from typing import Any

from app.domains.personal.future_building.quick_add.constants import (
    FUTURE_BUILDING_TAB_FIELDS,
)
from app.domains.personal.lifestyle.quick_add.constants import LIFESTYLE_TAB_FIELDS
from app.domains.personal.relationships.quick_add.constants import RELATIONSHIPS_TAB_FIELDS
from app.domains.personal.life_operations.quick_add.constants import EVENT_TO_TAB

_LO_EDIT_FIELDS: dict[str, list[dict[str, Any]]] = {
    "EXPENSE": [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "amount", "label": "Amount", "field_type": "amount", "path": "expense.amount"},
        {"key": "account_id", "label": "Account", "field_type": "account", "path": "expense.account_id"},
        {"key": "category_name", "label": "Category", "field_type": "text", "path": "expense.category_name"},
        {"key": "event_summary", "label": "Note", "field_type": "textarea"},
    ],
    "REFLECTION": [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "feeling_state", "label": "Feeling", "field_type": "single_select", "path": "reflection.feeling_state"},
        {"key": "reflection_note", "label": "Note", "field_type": "textarea", "path": "reflection.reflection_note"},
    ],
    "RECOVERY": [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "recovery_type", "label": "Type", "field_type": "text", "path": "recovery.recovery_type"},
        {"key": "notes", "label": "Note", "field_type": "textarea", "path": "recovery.notes"},
    ],
    "COMMITMENT": [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "event_summary", "label": "Note", "field_type": "textarea"},
    ],
    "RHYTHM": [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "event_summary", "label": "Note", "field_type": "textarea"},
    ],
}


def _fb_fields_for_event(event_type: str) -> list[dict[str, Any]]:
    upper = event_type.upper()
    for tab in FUTURE_BUILDING_TAB_FIELDS:
        if tab.get("event_type") == upper:
            fields: list[dict[str, Any]] = [
                {
                    "key": "event_title",
                    "label": "Title",
                    "field_type": "text",
                    "required": True,
                }
            ]
            for group in tab.get("field_groups") or []:
                fields.append(
                    {
                        "key": str(group.get("group_key") or ""),
                        "label": str(group.get("label") or ""),
                        "field_type": str(group.get("field_type") or "text"),
                        "required": bool(group.get("required")),
                        "path": f"future_building.{group.get('group_key')}",
                        "options": group.get("options"),
                    }
                )
            fields.append(
                {
                    "key": "event_summary",
                    "label": "Note",
                    "field_type": "textarea",
                }
            )
            if upper == "CONTRIBUTION":
                fields.insert(
                    1,
                    {
                        "key": "amount",
                        "label": "Amount",
                        "field_type": "amount",
                        "path": "expense.amount",
                    },
                )
            return fields
    return [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "event_summary", "label": "Note", "field_type": "textarea"},
    ]


def _ls_fields_for_event(event_type: str) -> list[dict[str, Any]]:
    upper = event_type.upper()
    for tab in LIFESTYLE_TAB_FIELDS:
        if tab.get("event_type") == upper:
            fields: list[dict[str, Any]] = [
                {
                    "key": "event_title",
                    "label": "Title",
                    "field_type": "text",
                    "required": True,
                }
            ]
            for group in tab.get("field_groups") or []:
                fields.append(
                    {
                        "key": str(group.get("group_key") or ""),
                        "label": str(group.get("label") or ""),
                        "field_type": str(group.get("field_type") or "text"),
                        "required": bool(group.get("required")),
                        "path": f"lifestyle.{group.get('group_key')}",
                        "options": group.get("options"),
                    }
                )
            fields.append(
                {
                    "key": "event_summary",
                    "label": "Note",
                    "field_type": "textarea",
                }
            )
            if upper == "LIFESTYLE_EXPENSE":
                fields.insert(
                    1,
                    {
                        "key": "amount",
                        "label": "Amount",
                        "field_type": "amount",
                        "path": "expense.amount",
                    },
                )
            return fields
    return [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "event_summary", "label": "Note", "field_type": "textarea"},
    ]


def _rs_fields_for_event(event_type: str) -> list[dict[str, Any]]:
    upper = event_type.upper()
    if upper == "RELATIONSHIP_ADJUST":
        upper = "ADJUST"
    for tab in RELATIONSHIPS_TAB_FIELDS:
        if tab.get("event_type") == upper:
            fields: list[dict[str, Any]] = [
                {
                    "key": "event_title",
                    "label": "Title",
                    "field_type": "text",
                    "required": True,
                }
            ]
            for group in tab.get("field_groups") or []:
                fields.append(
                    {
                        "key": str(group.get("group_key") or ""),
                        "label": str(group.get("label") or ""),
                        "field_type": str(group.get("field_type") or "text"),
                        "required": bool(group.get("required")),
                        "path": f"relationships.{group.get('group_key')}",
                        "options": group.get("options"),
                    }
                )
            fields.append(
                {
                    "key": "event_summary",
                    "label": "Note",
                    "field_type": "textarea",
                }
            )
            if upper in {"SHARED_EXPERIENCE", "RELATIONSHIP_INVESTMENT"}:
                fields.insert(
                    1,
                    {
                        "key": "amount",
                        "label": "Amount",
                        "field_type": "amount",
                        "path": "expense.amount",
                    },
                )
            return fields
    return [
        {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
        {"key": "event_summary", "label": "Note", "field_type": "textarea"},
    ]


def build_edit_schema(moment_type_code: str, event_type: str) -> dict[str, Any]:
    upper = event_type.upper()
    if moment_type_code == "FUTURE_BUILDING":
        fields = _fb_fields_for_event(upper)
    elif moment_type_code == "LIFESTYLE":
        fields = _ls_fields_for_event(upper)
    elif moment_type_code == "RELATIONSHIPS":
        fields = _rs_fields_for_event(upper)
    elif moment_type_code == "LIFE_OPERATIONS":
        fields = _LO_EDIT_FIELDS.get(
            upper,
            [
                {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
                {"key": "event_summary", "label": "Note", "field_type": "textarea"},
            ],
        )
    else:
        fields = [
            {"key": "event_title", "label": "Title", "field_type": "text", "required": True},
            {"key": "event_summary", "label": "Note", "field_type": "textarea"},
        ]
    return {
        "event_type": upper,
        "supported_event_types": list(EVENT_TO_TAB.keys()) if moment_type_code == "LIFE_OPERATIONS" else [],
        "fields": fields,
        "allowed_actions": ["edit", "delete"],
    }
