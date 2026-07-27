"""Build Future Building quick-add options."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import UUID

from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.future_building.quick_add.constants import (
    FIELD_GROUP_OPTIONS_KEY,
    FUTURE_BUILDING_QUICK_ADD_METADATA,
    FUTURE_BUILDING_QUICK_ADD_TABS,
    PIVOT_CONFIDENCE_OPTIONS_KEY,
)
from app.domains.reference_data.catalog import ReferenceCatalog


def _option_dicts(labels: list[str]) -> list[dict[str, str]]:
    return [{"value": label, "label": label} for label in labels]


def _hydrate_field_groups(
    metadata: dict[str, Any],
    *,
    expense_categories: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach options onto each select/chip_grid group from metadata + catalogs."""
    tabs = deepcopy(metadata.get("future_building_tabs") or [])
    category_options = []
    for cat in expense_categories:
        value = str(cat.get("name") or cat.get("code") or cat.get("label") or "").strip()
        if not value:
            continue
        label = str(cat.get("label") or cat.get("name") or value).strip()
        category_options.append({"value": value, "label": label})

    for tab in tabs:
        event_type = tab.get("event_type")
        for group in tab.get("field_groups") or []:
            if group.get("options"):
                continue
            key = group.get("group_key")
            field_type = group.get("field_type")
            if key == "category_name":
                if category_options:
                    group["options"] = category_options
                continue
            if field_type not in ("single_select", "chip_grid", "slider"):
                continue
            meta_key = FIELD_GROUP_OPTIONS_KEY.get(key or "")
            if key == "confidence_level" and event_type == "PIVOT":
                meta_key = PIVOT_CONFIDENCE_OPTIONS_KEY
            if not meta_key:
                continue
            labels = metadata.get(meta_key) or []
            if labels:
                group["options"] = _option_dicts(list(labels))
    return tabs


class FutureBuildingQuickAddOptionsBuilder:
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
        expense_categories = catalog.get("expense_categories", active_only=True)
        metadata = dict(FUTURE_BUILDING_QUICK_ADD_METADATA)
        metadata["future_building_tabs"] = _hydrate_field_groups(
            FUTURE_BUILDING_QUICK_ADD_METADATA,
            expense_categories=expense_categories,
        )
        return {
            "moments": moment_options,
            "tabs": FUTURE_BUILDING_QUICK_ADD_TABS,
            "categories": [],
            "accounts": accounts,
            "entries_today_count": entries_today_count,
            "default_currency_code": default_currency_code,
            "currencies": catalog.get("currencies", active_only=True),
            "expense_categories": expense_categories,
            "account_types": catalog.get("account_types", active_only=True),
            "metadata": metadata,
        }
