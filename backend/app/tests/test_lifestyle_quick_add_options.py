"""Lifestyle quick-add options/metadata contract tests."""

from app.domains.personal.lifestyle.quick_add.constants import (
    FIELD_GROUP_OPTIONS_KEY,
    LIFESTYLE_QUICK_ADD_METADATA,
    LIFESTYLE_QUICK_ADD_TABS,
)
from app.domains.personal.lifestyle.quick_add.options_builder import _hydrate_field_groups


def test_tabs_have_guiding_questions_and_ctas():
    by_type = {t["event_type"]: t for t in LIFESTYLE_QUICK_ADD_TABS}
    assert by_type["LIFESTYLE_EXPENSE"]["hero_subtitle"] == "What was this expense for?"
    assert by_type["EXPRESSION"]["label"] == "Create"
    assert by_type["ADJUST"]["cta_label"] == "Update Lifestyle"
    assert "Record lifestyle spending" in by_type["LIFESTYLE_EXPENSE"]["description"]


def test_metadata_exposes_existing_option_lists():
    meta = LIFESTYLE_QUICK_ADD_METADATA
    assert "Memorable" in meta["experience_quality_options"]
    assert "Energized" in meta["energy_impact_options"]
    assert "Alone" in meta["people_context_options"]
    assert "Home" in meta["location_context_options"]
    assert "More Rest" in meta["adjustment_area_options"]
    assert "Somewhat Sure" in meta["confidence_level_options"]
    assert any(o["value"] == "30_60" for o in meta["time_invested_options"])


def test_hydrate_attaches_options():
    tabs = _hydrate_field_groups(LIFESTYLE_QUICK_ADD_METADATA)
    exp = next(t for t in tabs if t["event_type"] == "EXPERIENCE")
    quality = next(g for g in exp["field_groups"] if g["group_key"] == "experience_quality")
    assert quality["options"]
    assert quality["field_type"] == "chip_grid"

    expense = next(t for t in tabs if t["event_type"] == "LIFESTYLE_EXPENSE")
    category = next(g for g in expense["field_groups"] if g["group_key"] == "spend_category")
    assert any(o["value"] == "Travel" for o in category["options"])


def test_field_group_options_key_coverage():
    for key in (
        "spend_category",
        "experience_quality",
        "energy_impact",
        "wellbeing_areas",
        "curiosity_level",
        "satisfaction_level",
        "time_invested",
        "adjustment_area",
    ):
        assert key in FIELD_GROUP_OPTIONS_KEY
