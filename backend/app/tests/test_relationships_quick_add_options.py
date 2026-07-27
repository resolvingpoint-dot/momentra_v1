"""Relationships quick-add options hydration tests."""
from __future__ import annotations

from uuid import uuid4

from app.domains.personal.relationships.quick_add.constants import (
    FIELD_GROUP_OPTIONS_KEY,
    RELATIONSHIPS_QUICK_ADD_METADATA,
)
from app.domains.personal.relationships.quick_add.options_builder import (
    RelationshipsQuickAddOptionsBuilder,
    _hydrate_field_groups,
)
from app.domains.reference_data.catalog import get_reference_catalog


def test_hydrate_field_groups_attaches_chip_options():
    tabs = _hydrate_field_groups(RELATIONSHIPS_QUICK_ADD_METADATA)
    by_type = {t["event_type"]: t for t in tabs}

    connection = by_type["CONNECTION"]
    groups = {g["group_key"]: g for g in connection["field_groups"]}
    assert groups["connection_type"]["options"]
    assert groups["connection_quality"]["options"]
    assert groups["emotional_tone"]["options"]
    assert groups["relationship_type"]["options"]

    support = by_type["SUPPORT"]
    support_groups = {g["group_key"]: g for g in support["field_groups"]}
    assert support_groups["support_direction"]["options"]
    assert {o["value"] for o in support_groups["support_direction"]["options"]} == {
        "Given",
        "Received",
        "Mutual",
    }

    shared = by_type["SHARED_EXPERIENCE"]
    shared_groups = {g["group_key"]: g for g in shared["field_groups"]}
    assert shared_groups["experience_type"]["options"]
    assert shared_groups["value_received"]["options"]
    assert shared_groups["spend_category"]["options"]
    # Notes no longer marked required in schema (title can satisfy narrative).
    assert not shared_groups["notes"].get("required")

    adjust = by_type["ADJUST"]
    adjust_groups = {g["group_key"]: g for g in adjust["field_groups"]}
    assert adjust_groups["adjustment_area"]["options"]
    assert adjust_groups["priority_level"]["options"]
    assert not adjust_groups["notes"].get("required")


def test_field_group_options_key_covers_select_fields():
    for tab in RELATIONSHIPS_QUICK_ADD_METADATA["emotional_security_tabs"]:
        for group in tab["field_groups"]:
            if group["field_type"] in ("chip_grid", "single_select"):
                assert group["group_key"] in FIELD_GROUP_OPTIONS_KEY


def test_options_builder_returns_hydrated_metadata():
    catalog = get_reference_catalog()
    built = RelationshipsQuickAddOptionsBuilder().build(
        user_id=uuid4(),
        moments=[],
        accounts=[],
        entries_today_count=0,
        default_currency_code="INR",
        catalog=catalog,
    )
    tabs = built["metadata"]["emotional_security_tabs"]
    connection = next(t for t in tabs if t["event_type"] == "CONNECTION")
    connection_type = next(g for g in connection["field_groups"] if g["group_key"] == "connection_type")
    assert len(connection_type["options"]) >= 3
    assert built["tabs"][0]["cta_label"] == "Save Shared Experience"
    assert built["tabs"][0].get("guiding_question")


def test_notes_for_falls_back_to_event_title():
    from types import SimpleNamespace

    from app.domains.personal.relationships.quick_add.handlers.base import notes_for

    ctx = SimpleNamespace(event_title="Dinner with family", body={})
    assert notes_for(ctx, {}) == "Dinner with family"
    assert notes_for(ctx, {"notes": "custom"}) == "custom"
    assert notes_for(SimpleNamespace(event_title="", body={}), {}) is None
