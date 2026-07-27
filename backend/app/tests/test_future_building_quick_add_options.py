"""Future Building quick-add options/metadata contract tests."""

from app.domains.personal.future_building.quick_add.constants import (
    FIELD_GROUP_OPTIONS_KEY,
    FUTURE_BUILDING_QUICK_ADD_METADATA,
    FUTURE_BUILDING_QUICK_ADD_TABS,
)
from app.domains.personal.future_building.quick_add.options_builder import _hydrate_field_groups


def test_tabs_have_guiding_questions_and_unified_ctas():
    by_type = {t["event_type"]: t for t in FUTURE_BUILDING_QUICK_ADD_TABS}
    assert by_type["CONTRIBUTION"]["hero_subtitle"] == "What did you invest in?"
    assert by_type["MILESTONE"]["cta_label"] == "Save Milestone"
    assert by_type["OPPORTUNITY"]["cta_label"] == "Save Opportunity"
    assert by_type["PIVOT"]["cta_label"] == "Save Pivot"
    assert by_type["PROGRESS"]["cta_label"] == "Save Progress"
    assert "Put in money" in by_type["CONTRIBUTION"]["description"]


def test_metadata_exposes_existing_enum_option_lists():
    meta = FUTURE_BUILDING_QUICK_ADD_METADATA
    assert "Personal Win" in meta["celebration_level_options"]
    assert "Income Increase" in meta["outcome_value_options"]
    assert "Change Direction" in meta["pivot_change_options"]
    assert "New Information" in meta["pivot_reason_options"]
    assert "Exceptional" in meta["effort_level_options"]
    assert "High Leverage" in meta["relevance_level_options"]
    assert "Game-Changing" in meta["potential_level_options"]
    assert "15 min" in meta["time_invested_options"]


def test_hydrate_attaches_options_to_chip_and_select_groups():
    tabs = _hydrate_field_groups(
        FUTURE_BUILDING_QUICK_ADD_METADATA,
        expense_categories=[
            {"code": "HEALTH", "label": "Health", "name": "Health"},
        ],
    )
    contrib = next(t for t in tabs if t["event_type"] == "CONTRIBUTION")
    category = next(g for g in contrib["field_groups"] if g["group_key"] == "category_name")
    impact = next(g for g in contrib["field_groups"] if g["group_key"] == "impact_level")
    assert category["options"]
    assert impact["options"]
    assert impact["options"][0]["value"] == impact["options"][0]["label"]

    pivot = next(t for t in tabs if t["event_type"] == "PIVOT")
    confidence = next(g for g in pivot["field_groups"] if g["group_key"] == "confidence_level")
    assert any(o["value"] == "Medium" for o in confidence["options"])

    opp = next(t for t in tabs if t["event_type"] == "OPPORTUNITY")
    opp_conf = next(g for g in opp["field_groups"] if g["group_key"] == "confidence_level")
    assert any(o["value"] == "Game-Changing" for o in opp_conf["options"])


def test_field_group_options_key_covers_chip_fields():
    for key in (
        "celebration_level",
        "outcome_value",
        "effort_level",
        "relevance",
        "pivot_change",
        "time_invested",
    ):
        assert key in FIELD_GROUP_OPTIONS_KEY
