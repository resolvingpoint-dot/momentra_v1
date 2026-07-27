"""JSON draft envelope stored on shared ``moments.description``."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.domains.moments.models import MomentModel

SETUP_VERSION_DEFAULT = "1"
TEMPLATE_VERSION_DEFAULT = "1"

_DEFAULT_ANSWERS: dict[str, Any] = {
    "country_code": None,
    "locale": None,
    "timezone": None,
    "default_currency_code": None,
    "operating_currency_code": None,
    "allow_multi_currency": False,
    "financial_year_start": None,
    "members": [],
    "member_drafts": [],
    "supported_roles": [
        "OWNER",
        "ADMIN",
        "TEAM_LEAD",
        "OPERATIONS_LEAD",
        "FINANCE_LEAD",
        "BUDGET_OWNER",
        "APPROVER",
        "CONTRIBUTOR",
        "MEMBER",
        "OBSERVER",
    ],
    "invite_on_activation": True,
    "notify_members": True,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_envelope(
    *,
    template_id: str,
    template_version: str = TEMPLATE_VERSION_DEFAULT,
    setup_version: str = SETUP_VERSION_DEFAULT,
) -> dict[str, Any]:
    return {
        "setup_version": str(setup_version),
        "template_id": template_id,
        "template_version": str(template_version),
        "answers": dict(_DEFAULT_ANSWERS),
        "progress": {"current_step": 1, "completed_steps": []},
        "membership": [],
        "activated_at": None,
        "updated_at": _now_iso(),
    }


def read_envelope(moment: MomentModel) -> dict[str, Any]:
    raw = moment.description or ""
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_envelope(moment: MomentModel, envelope: dict[str, Any]) -> None:
    envelope = dict(envelope)
    envelope["updated_at"] = _now_iso()
    moment.description = json.dumps(envelope)
    moment.updated_at = datetime.now(timezone.utc)


def merge_answers(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge one level; preserve unknown keys from both sides."""
    merged = dict(existing or {})
    for key, value in (incoming or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged
