from app.services.nlp_service import nlp_service
from app.services.dealshield_export import render_dealshield_html
from app.v2.config.master_config import BuildingType, ProjectClass
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


def _calculate_project(**kwargs):
    return unified_engine.calculate_project(
        building_type=kwargs.get("building_type", BuildingType.RETAIL),
        subtype=kwargs.get("subtype", "shopping_center"),
        square_footage=kwargs.get("square_footage", 95000),
        location=kwargs.get("location", "Nashville, TN"),
        project_class=kwargs.get("project_class", ProjectClass.GROUND_UP),
        floors=kwargs.get("floors", 2),
        ownership_type=kwargs.get("ownership_type", "for_profit"),
        finish_level=kwargs.get("finish_level", "standard"),
        finish_level_source=kwargs.get("finish_level_source", "explicit"),
        special_features=kwargs.get("special_features", []),
        parsed_input_overrides=kwargs.get("parsed_input_overrides", {}),
    )


def test_nlp_parser_extracts_type_subtype_and_floors():
    description = "New 120,000 sf big box retail store, 2-story, Nashville TN"
    parsed = nlp_service.extract_project_details(description)

    assert parsed.get("building_type") == "retail"
    assert parsed.get("subtype") in {"big_box", "big_box_retail"}
    assert parsed.get("floors") == 2


def test_project_class_and_finish_level_inference_from_description():
    description = "Renovation of a luxury medical office building in Manchester NH"
    result = unified_engine.estimate_from_description(
        description=description,
        square_footage=45000,
        location="Manchester, NH",
    )

    project_info = result.get("project_info") or {}
    assert project_info.get("project_class") == "renovation"
    assert project_info.get("finish_level") == "luxury"
    assert project_info.get("finish_level_source") == "description"


def test_special_features_breakdown_present():
    result = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=95000,
        location="Nashville, TN",
        finish_level="premium",
        special_features=["covered_walkway", "drive_thru"],
    )

    breakdown = (result.get("construction_costs") or {}).get("special_features_breakdown") or []
    feature_ids = {row.get("id") for row in breakdown}
    assert {"covered_walkway", "drive_thru"}.issubset(feature_ids)


def test_floor_count_reflects_request():
    result = _calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=85000,
        location="Nashville, TN",
        floors=6,
        finish_level="standard",
    )

    project_info = result.get("project_info") or {}
    assert project_info.get("floors") == 6


def test_regional_multiplier_changes_with_location():
    base = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=35000,
        location="Nashville, TN",
    )
    alt = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=35000,
        location="Manchester, NH",
    )

    base_mult = (base.get("regional") or {}).get("multiplier")
    alt_mult = (alt.get("regional") or {}).get("multiplier")
    assert isinstance(base_mult, (int, float))
    assert isinstance(alt_mult, (int, float))
    assert base_mult != alt_mult


def test_dealshield_scenarios_present_for_retail_profiles():
    result = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=35000,
        location="Nashville, TN",
    )

    scenarios = result.get("dealshield_scenarios") or {}
    assert isinstance(scenarios, dict)
    assert "scenarios" in scenarios
    assert "base" in (scenarios.get("scenarios") or {})


def test_export_dealshield_html_renders():
    payload = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=35000,
        location="Nashville, TN",
    )
    profile_id = payload.get("dealshield_tile_profile") or "retail_shopping_center_v1"
    profile = get_dealshield_profile(profile_id)
    view_model = build_dealshield_view_model("proj_test_export", payload, profile)
    html = render_dealshield_html(view_model)

    assert isinstance(html, str)
    assert "DealShield" in html
