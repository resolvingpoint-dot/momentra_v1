"""Build Lifestyle quick-add options."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID

from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.lifestyle.quick_add.constants import (
    FIELD_GROUP_OPTIONS_KEY,
    LIFESTYLE_QUICK_ADD_METADATA,
    LIFESTYLE_QUICK_ADD_TABS,
)
from app.domains.reference_data.catalog import ReferenceCatalog


def _option_dicts(raw: list[Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in raw:
        if isinstance(item, dict):
            value = str(item.get("value") or item.get("label") or "").strip()
            label = str(item.get("label") or value).strip()
            if value:
                out.append({"value": value, "label": label})
        else:
            label = str(item).strip()
            if label:
                out.append({"value": label, "label": label})
    return out


def _hydrate_field_groups(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    tabs = deepcopy(metadata.get("lifestyle_tabs") or [])
    for tab in tabs:
        for group in tab.get("field_groups") or []:
            if group.get("options"):
                continue
            key = group.get("group_key")
            field_type = group.get("field_type")
            if field_type not in ("single_select", "chip_grid", "slider", "multi_select"):
                continue
            meta_key = FIELD_GROUP_OPTIONS_KEY.get(key or "")
            if not meta_key:
                continue
            raw = metadata.get(meta_key) or []
            opts = _option_dicts(list(raw))
            if opts:
                group["options"] = opts
    return tabs


class LifestyleQuickAddOptionsBuilder:
    def build(
        self,
        *,
        user_id: UUID,
        moments: list[MomentModel],
        accounts: list[dict[str, Any]],
        entries_today_count: int,
        default_currency_code: str,
        catalog: ReferenceCatalog,
    ) -> dict[str, Any]:
        del user_id
        moment_options = [
            {
                "moment_id": str(m.id),
                "moment_name": m.title or "Untitled",
                "moment_type_code": normalize_moment_type_code(m.moment_type or ""),
            }
            for m in moments
        ]
        metadata = dict(LIFESTYLE_QUICK_ADD_METADATA)
        metadata["lifestyle_tabs"] = _hydrate_field_groups(LIFESTYLE_QUICK_ADD_METADATA)
        return {
            "moments": moment_options,
            "tabs": LIFESTYLE_QUICK_ADD_TABS,
            "categories": [],
            "accounts": accounts,
            "entries_today_count": entries_today_count,
            "default_currency_code": default_currency_code,
            "currencies": catalog.get("currencies", active_only=True),
            "expense_categories": catalog.get("expense_categories", active_only=True),
            "account_types": catalog.get("account_types", active_only=True),
            "metadata": metadata,
        }
