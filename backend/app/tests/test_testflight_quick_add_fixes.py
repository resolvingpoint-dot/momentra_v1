"""Unit tests for Learning / Connection / Lifestyle spend mapping fixes."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.learning import (
    resolve_application_status,
)
from app.domains.personal.quick_add.enum_utils import as_note
from app.domains.personal.quick_add.money import resolve_spend_category_code
from app.domains.personal.relationships.quick_add.handlers.connection import (
    resolve_optional_enum,
)
from app.domains.personal.relationships.quick_add.handlers.mappings import (
    EMOTIONAL_TONE_ALIASES,
    EMOTIONAL_TONE_VALUES,
    TIME_INVESTED_ALIASES,
    TIME_INVESTED_VALUES,
)
from app.domains.personal.relationships.quick_add.options_builder import _hydrate_field_groups
from app.domains.personal.relationships.quick_add.constants import (
    RELATIONSHIPS_QUICK_ADD_METADATA,
)


def test_learning_application_free_text_not_status():
    assert resolve_application_status("In my current job") is None
    assert resolve_application_status("Will Use Soon") == "Will Use Soon"
    assert resolve_application_status("Already Applying") == "Already Applying"
    note = as_note("Topic", "In my current job", "extra")
    assert "In my current job" in (note or "")


def test_connection_tone_and_time_map_to_db_codes():
    assert (
        resolve_optional_enum(
            "Warm",
            valid=EMOTIONAL_TONE_VALUES,
            aliases=EMOTIONAL_TONE_ALIASES,
        )
        == "Positive"
    )
    assert (
        resolve_optional_enum(
            "5 min",
            valid=TIME_INVESTED_VALUES,
            aliases=TIME_INVESTED_ALIASES,
        )
        == "<15"
    )
    assert (
        resolve_optional_enum(
            "<15",
            valid=TIME_INVESTED_VALUES,
            aliases=TIME_INVESTED_ALIASES,
        )
        == "<15"
    )


def test_connection_options_time_values_are_db_codes():
    tabs = _hydrate_field_groups(RELATIONSHIPS_QUICK_ADD_METADATA)
    connection = next(t for t in tabs if t["event_type"] == "CONNECTION")
    groups = {g["group_key"]: g for g in connection["field_groups"]}
    time_values = {o["value"] for o in groups["time_invested"]["options"]}
    assert time_values <= TIME_INVESTED_VALUES
    assert "<15" in time_values
    tone_labels = {o["label"] for o in groups["emotional_tone"]["options"]}
    assert "Warm" in tone_labels


def test_lifestyle_spend_category_maps_to_taxonomy():
    assert resolve_spend_category_code("Food & Dining") == "FOOD"
    assert resolve_spend_category_code("Travel") == "TRANSPORT"
    assert resolve_spend_category_code("Wellbeing") == "HEALTH"
    assert resolve_spend_category_code("FOOD") == "FOOD"
    assert resolve_spend_category_code("Unknown Thing") is None
