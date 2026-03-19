import pytest

from app.services.nlp_service import nlp_service
from app.services.dealshield_export import render_dealshield_html
from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
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


def _area_share_rule(config, feature_id):
    feature_rule = config.special_features[feature_id]
    assert isinstance(feature_rule, dict)
    return feature_rule


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


def test_project_info_exposes_available_special_feature_pricing_for_current_subtype():
    config = get_building_config(BuildingType.HOSPITALITY, "full_service_hotel")
    assert config is not None
    result = _calculate_project(
        building_type=BuildingType.HOSPITALITY,
        subtype="full_service_hotel",
        square_footage=85000,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["ballroom", "spa"],
    )

    project_info = result.get("project_info") or {}
    available_pricing = project_info.get("available_special_feature_pricing") or []
    pricing_by_id = {
        row.get("id"): row
        for row in available_pricing
        if isinstance(row, dict) and row.get("id")
    }

    assert "ballroom" in pricing_by_id
    assert "spa" in pricing_by_id
    assert pricing_by_id["ballroom"].get("pricing_status") == "included_in_baseline"
    assert pricing_by_id["spa"].get("pricing_status") == "incremental"
    assert pricing_by_id["ballroom"].get("pricing_basis") == "AREA_SHARE_GSF"
    assert pricing_by_id["spa"].get("pricing_basis") == "AREA_SHARE_GSF"
    assert pricing_by_id["ballroom"].get("configured_value") == _area_share_rule(config, "ballroom")["value"]
    assert pricing_by_id["spa"].get("configured_value") == _area_share_rule(config, "spa")["value"]
    assert pricing_by_id["ballroom"].get("configured_area_share_of_gsf") == _area_share_rule(config, "ballroom")["area_share_of_gsf"]
    assert pricing_by_id["spa"].get("configured_area_share_of_gsf") == _area_share_rule(config, "spa")["area_share_of_gsf"]


def test_medium_shopping_center_prices_only_incremental_features_and_preserves_statuses():
    square_footage = 48_000
    config = get_building_config(BuildingType.RETAIL, "shopping_center")
    assert config is not None
    covered_walkway_rule = _area_share_rule(config, "covered_walkway")
    drive_thru_rule = config.special_features["drive_thru"]
    assert isinstance(drive_thru_rule, dict)
    result = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=square_footage,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["covered_walkway", "drive_thru"],
    )

    construction_costs = result.get("construction_costs") or {}
    assert construction_costs.get("special_features_total") == pytest.approx(
        drive_thru_rule["value"] * drive_thru_rule["count"]
    )

    breakdown = construction_costs.get("special_features_breakdown") or []
    breakdown_by_id = {
        row.get("id"): row
        for row in breakdown
        if isinstance(row, dict) and row.get("id")
    }

    included_row = breakdown_by_id["covered_walkway"]
    assert included_row.get("pricing_status") == "included_in_baseline"
    assert included_row.get("pricing_basis") == "AREA_SHARE_GSF"
    assert included_row.get("configured_value") == pytest.approx(covered_walkway_rule["value"])
    assert included_row.get("configured_area_share_of_gsf") == pytest.approx(
        covered_walkway_rule["area_share_of_gsf"]
    )
    assert included_row.get("applied_value") == 0
    assert included_row.get("total_cost") == 0

    incremental_row = breakdown_by_id["drive_thru"]
    assert incremental_row.get("pricing_status") == "incremental"
    assert incremental_row.get("pricing_basis") == "COUNT_BASED"
    assert incremental_row.get("configured_cost_per_count") == drive_thru_rule["value"]
    assert incremental_row.get("applied_quantity") == drive_thru_rule["count"]
    assert incremental_row.get("quantity_source") == "configured_default_count"
    assert incremental_row.get("total_cost") == pytest.approx(
        drive_thru_rule["value"] * drive_thru_rule["count"]
    )


def test_medium_medical_office_building_statuses_zero_ready_shell_but_price_buildout():
    square_footage = 36_000
    result = _calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="medical_office_building",
        square_footage=square_footage,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["mob_imaging_ready_shell", "ambulatory_buildout"],
    )

    construction_costs = result.get("construction_costs") or {}
    assert construction_costs.get("special_features_total") == 60 * square_footage

    breakdown = construction_costs.get("special_features_breakdown") or []
    breakdown_by_id = {
        row.get("id"): row
        for row in breakdown
        if isinstance(row, dict) and row.get("id")
    }

    shell_row = breakdown_by_id["mob_imaging_ready_shell"]
    assert shell_row.get("pricing_status") == "included_in_baseline"
    assert shell_row.get("configured_cost_per_sf") == 40
    assert shell_row.get("cost_per_sf") == 0
    assert shell_row.get("total_cost") == 0

    buildout_row = breakdown_by_id["ambulatory_buildout"]
    assert buildout_row.get("pricing_status") == "incremental"
    assert buildout_row.get("configured_cost_per_sf") == 60
    assert buildout_row.get("cost_per_sf") == 60
    assert buildout_row.get("total_cost") == 60 * square_footage


def test_project_info_exposes_available_special_feature_pricing_for_medium_subtype():
    config = get_building_config(BuildingType.RETAIL, "shopping_center")
    assert config is not None
    result = _calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=95_000,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["covered_walkway", "drive_thru"],
    )

    project_info = result.get("project_info") or {}
    available_pricing = project_info.get("available_special_feature_pricing") or []
    pricing_by_id = {
        row.get("id"): row
        for row in available_pricing
        if isinstance(row, dict) and row.get("id")
    }

    assert pricing_by_id["covered_walkway"].get("pricing_status") == "included_in_baseline"
    assert pricing_by_id["covered_walkway"].get("pricing_basis") == "AREA_SHARE_GSF"
    assert pricing_by_id["covered_walkway"].get("configured_value") == pytest.approx(
        _area_share_rule(config, "covered_walkway")["value"]
    )
    assert pricing_by_id["covered_walkway"].get("configured_area_share_of_gsf") == pytest.approx(
        _area_share_rule(config, "covered_walkway")["area_share_of_gsf"]
    )
    assert pricing_by_id["drive_thru"].get("pricing_status") == "incremental"
    assert pricing_by_id["drive_thru"].get("pricing_basis") == "COUNT_BASED"
    assert pricing_by_id["drive_thru"].get("configured_cost_per_count") == pytest.approx(
        config.special_features["drive_thru"]["value"]
    )
    assert pricing_by_id["drive_thru"].get("configured_count") == pytest.approx(
        config.special_features["drive_thru"]["count"]
    )


def test_low_market_rate_apartments_features_remain_visible_and_price_as_incremental():
    square_footage = 64_000
    config = get_building_config(BuildingType.MULTIFAMILY, "market_rate_apartments")
    assert config is not None
    rooftop_rule = _area_share_rule(config, "rooftop_amenity")
    pool_rule = _area_share_rule(config, "pool")
    result = _calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=square_footage,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["rooftop_amenity", "pool"],
    )

    construction_costs = result.get("construction_costs") or {}
    expected_total = (
        rooftop_rule["value"] * (rooftop_rule["area_share_of_gsf"] * square_footage)
        + pool_rule["value"] * (pool_rule["area_share_of_gsf"] * square_footage)
    )
    assert construction_costs.get("special_features_total") == pytest.approx(expected_total)

    breakdown = construction_costs.get("special_features_breakdown") or []
    breakdown_by_id = {
        row.get("id"): row
        for row in breakdown
        if isinstance(row, dict) and row.get("id")
    }

    rooftop_row = breakdown_by_id["rooftop_amenity"]
    assert rooftop_row.get("pricing_status") == "incremental"
    assert rooftop_row.get("pricing_basis") == "AREA_SHARE_GSF"
    assert rooftop_row.get("configured_value") == pytest.approx(rooftop_rule["value"])
    assert rooftop_row.get("configured_area_share_of_gsf") == pytest.approx(rooftop_rule["area_share_of_gsf"])
    assert rooftop_row.get("applied_quantity") == pytest.approx(rooftop_rule["area_share_of_gsf"] * square_footage)
    assert rooftop_row.get("total_cost") == pytest.approx(rooftop_rule["value"] * (
        rooftop_rule["area_share_of_gsf"] * square_footage
    ))

    pool_row = breakdown_by_id["pool"]
    assert pool_row.get("pricing_status") == "incremental"
    assert pool_row.get("pricing_basis") == "AREA_SHARE_GSF"
    assert pool_row.get("configured_value") == pytest.approx(pool_rule["value"])
    assert pool_row.get("configured_area_share_of_gsf") == pytest.approx(pool_rule["area_share_of_gsf"])
    assert pool_row.get("applied_quantity") == pytest.approx(pool_rule["area_share_of_gsf"] * square_footage)
    assert pool_row.get("total_cost") == pytest.approx(pool_rule["value"] * (
        pool_rule["area_share_of_gsf"] * square_footage
    ))


def test_low_limited_service_hotel_features_remain_incremental():
    square_footage = 52_000
    config = get_building_config(BuildingType.HOSPITALITY, "limited_service_hotel")
    assert config is not None
    breakfast_rule = _area_share_rule(config, "breakfast_area")
    pool_rule = _area_share_rule(config, "pool")
    result = _calculate_project(
        building_type=BuildingType.HOSPITALITY,
        subtype="limited_service_hotel",
        square_footage=square_footage,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["breakfast_area", "pool"],
    )

    construction_costs = result.get("construction_costs") or {}
    expected_total = (
        breakfast_rule["value"] * (breakfast_rule["area_share_of_gsf"] * square_footage)
        + pool_rule["value"] * (pool_rule["area_share_of_gsf"] * square_footage)
    )
    assert construction_costs.get("special_features_total") == pytest.approx(expected_total)

    breakdown = construction_costs.get("special_features_breakdown") or []
    breakdown_by_id = {
        row.get("id"): row
        for row in breakdown
        if isinstance(row, dict) and row.get("id")
    }

    breakfast_row = breakdown_by_id["breakfast_area"]
    assert breakfast_row.get("pricing_status") == "incremental"
    assert breakfast_row.get("pricing_basis") == "AREA_SHARE_GSF"
    assert breakfast_row.get("configured_value") == pytest.approx(breakfast_rule["value"])
    assert breakfast_row.get("configured_area_share_of_gsf") == pytest.approx(
        breakfast_rule["area_share_of_gsf"]
    )
    assert breakfast_row.get("applied_quantity") == pytest.approx(
        breakfast_rule["area_share_of_gsf"] * square_footage
    )
    assert breakfast_row.get("total_cost") == pytest.approx(
        breakfast_rule["value"] * (breakfast_rule["area_share_of_gsf"] * square_footage)
    )

    pool_row = breakdown_by_id["pool"]
    assert pool_row.get("pricing_status") == "incremental"
    assert pool_row.get("pricing_basis") == "AREA_SHARE_GSF"
    assert pool_row.get("configured_value") == pytest.approx(pool_rule["value"])
    assert pool_row.get("configured_area_share_of_gsf") == pytest.approx(pool_rule["area_share_of_gsf"])
    assert pool_row.get("applied_quantity") == pytest.approx(pool_rule["area_share_of_gsf"] * square_footage)
    assert pool_row.get("total_cost") == pytest.approx(
        pool_rule["value"] * (pool_rule["area_share_of_gsf"] * square_footage)
    )


def test_project_info_exposes_available_special_feature_pricing_for_low_subtype():
    config = get_building_config(BuildingType.MULTIFAMILY, "market_rate_apartments")
    assert config is not None
    result = _calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=64_000,
        location="Nashville, TN",
        finish_level="standard",
        special_features=["rooftop_amenity", "pool"],
    )

    project_info = result.get("project_info") or {}
    available_pricing = project_info.get("available_special_feature_pricing") or []
    pricing_by_id = {
        row.get("id"): row
        for row in available_pricing
        if isinstance(row, dict) and row.get("id")
    }

    assert pricing_by_id["rooftop_amenity"].get("pricing_status") == "incremental"
    assert pricing_by_id["rooftop_amenity"].get("pricing_basis") == "AREA_SHARE_GSF"
    assert pricing_by_id["rooftop_amenity"].get("configured_value") == pytest.approx(_area_share_rule(config, "rooftop_amenity")["value"])
    assert pricing_by_id["rooftop_amenity"].get("configured_area_share_of_gsf") == pytest.approx(_area_share_rule(config, "rooftop_amenity")["area_share_of_gsf"])
    assert pricing_by_id["pool"].get("pricing_status") == "incremental"
    assert pricing_by_id["pool"].get("pricing_basis") == "AREA_SHARE_GSF"
    assert pricing_by_id["pool"].get("configured_value") == pytest.approx(_area_share_rule(config, "pool")["value"])
    assert pricing_by_id["pool"].get("configured_area_share_of_gsf") == pytest.approx(_area_share_rule(config, "pool")["area_share_of_gsf"])


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
