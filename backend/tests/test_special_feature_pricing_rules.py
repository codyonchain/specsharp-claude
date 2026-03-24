import pytest

from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    SpecialFeaturePricingBasis,
    get_building_config,
)
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.special_feature_pricing import (
    INCLUDED_IN_BASELINE,
    INCREMENTAL,
    LEGACY_FLOAT_NORMALIZATION_SOURCE,
    SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE,
    STRUCTURED_RULE_SOURCE,
    apply_special_feature_pricing_rule,
    normalize_special_feature_pricing_rule,
)


def _special_feature_breakdown_by_id(result):
    return {
        row["id"]: row
        for row in result["construction_costs"]["special_features_breakdown"]
        if isinstance(row, dict) and row.get("id")
    }


def _available_special_feature_pricing_by_id(result):
    return {
        row["id"]: row
        for row in result["project_info"]["available_special_feature_pricing"]
        if isinstance(row, dict) and row.get("id")
    }


def _scope_item_totals_by_trade(scope_items):
    totals = {}
    for item in scope_items or []:
        if not isinstance(item, dict):
            continue
        trade_key = str(item.get("trade") or "").strip().lower()
        if not trade_key:
            continue
        totals[trade_key] = sum(
            float(system.get("total_cost", 0.0) or 0.0)
            for system in item.get("systems", [])
            if isinstance(system, dict)
        )
    return totals


STAGE3_REMAINING_ACTIVE_SUBTYPES = (
    (BuildingType.HEALTHCARE, "hospital"),
    (BuildingType.HEALTHCARE, "medical_center"),
    (BuildingType.HEALTHCARE, "outpatient_clinic"),
    (BuildingType.HEALTHCARE, "urgent_care"),
    (BuildingType.HEALTHCARE, "surgical_center"),
    (BuildingType.HEALTHCARE, "imaging_center"),
    (BuildingType.HEALTHCARE, "medical_office_building"),
    (BuildingType.HEALTHCARE, "dental_office"),
    (BuildingType.HEALTHCARE, "rehabilitation"),
    (BuildingType.HEALTHCARE, "nursing_home"),
    (BuildingType.PARKING, "parking_garage"),
    (BuildingType.PARKING, "surface_parking"),
    (BuildingType.PARKING, "automated_parking"),
    (BuildingType.PARKING, "underground_parking"),
    (BuildingType.SPECIALTY, "data_center"),
    (BuildingType.SPECIALTY, "laboratory"),
    (BuildingType.SPECIALTY, "broadcast_facility"),
    (BuildingType.SPECIALTY, "car_dealership"),
    (BuildingType.SPECIALTY, "self_storage"),
    (BuildingType.EDUCATIONAL, "elementary_school"),
    (BuildingType.EDUCATIONAL, "middle_school"),
    (BuildingType.EDUCATIONAL, "high_school"),
    (BuildingType.EDUCATIONAL, "community_college"),
    (BuildingType.EDUCATIONAL, "university"),
    (BuildingType.RECREATION, "fitness_center"),
    (BuildingType.RECREATION, "recreation_center"),
    (BuildingType.RECREATION, "aquatic_center"),
    (BuildingType.RECREATION, "sports_complex"),
    (BuildingType.RECREATION, "stadium"),
    (BuildingType.CIVIC, "library"),
    (BuildingType.CIVIC, "community_center"),
    (BuildingType.CIVIC, "government_building"),
    (BuildingType.CIVIC, "public_safety"),
    (BuildingType.CIVIC, "courthouse"),
)


def test_legacy_float_rule_normalizes_to_whole_project_sf():
    rule = normalize_special_feature_pricing_rule("pool", 18)

    assert rule.feature_id == "pool"
    assert rule.basis == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF
    assert rule.configured_value == 18.0
    assert rule.assumption_source == LEGACY_FLOAT_NORMALIZATION_SOURCE


@pytest.mark.parametrize(
    ("pricing_status", "expected_cost_per_sf", "expected_total_cost"),
    (
        (INCREMENTAL, 24.0, 24.0 * 64_000.0),
        (INCLUDED_IN_BASELINE, 0.0, 0.0),
    ),
)
def test_whole_project_sf_rule_application_preserves_status_zeroing(
    pricing_status,
    expected_cost_per_sf,
    expected_total_cost,
):
    rule = normalize_special_feature_pricing_rule(
        "rooftop_amenity",
        {
            "basis": SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value,
            "value": 24,
        },
    )

    applied = apply_special_feature_pricing_rule(
        rule=rule,
        square_footage=64_000,
        pricing_status=pricing_status,
    )

    assert applied.pricing_basis == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF
    assert applied.configured_value == 24.0
    assert applied.configured_cost_per_sf == 24.0
    assert applied.cost_per_sf == expected_cost_per_sf
    assert applied.applied_quantity == 64_000.0
    assert applied.total_cost == pytest.approx(expected_total_cost)


def test_legacy_float_engine_breakdown_still_uses_normalized_whole_project_sf_for_deferred_feature():
    square_footage = 64_000
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="flex_space",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["heavy_power"],
    )

    construction_costs = result["construction_costs"]
    breakdown = construction_costs["special_features_breakdown"]
    breakdown_by_id = _special_feature_breakdown_by_id(result)
    heavy_power_row = breakdown_by_id["heavy_power"]

    assert construction_costs["special_features_total"] == pytest.approx(20.0 * square_footage)
    assert heavy_power_row["pricing_basis"] == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value
    assert heavy_power_row["configured_value"] == pytest.approx(20.0)
    assert heavy_power_row["applied_value"] == pytest.approx(20.0)
    assert heavy_power_row["applied_quantity"] == pytest.approx(square_footage)
    assert heavy_power_row["configured_cost_per_sf"] == pytest.approx(20.0)
    assert heavy_power_row["cost_per_sf"] == pytest.approx(20.0)
    assert heavy_power_row["assumption_source"] == LEGACY_FLOAT_NORMALIZATION_SOURCE
    assert heavy_power_row["total_cost"] == pytest.approx(20.0 * square_footage)
    assert sum(
        float(item.get("total_cost", 0.0) or 0.0)
        for item in breakdown
        if isinstance(item, dict)
    ) == pytest.approx(construction_costs["special_features_total"])


@pytest.mark.parametrize(
    ("building_type", "subtype", "expected_bases"),
    (
        (
            BuildingType.HOSPITALITY,
            "limited_service_hotel",
            {
                "breakfast_area": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "fitness_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "business_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "pool": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            },
        ),
        (
            BuildingType.MULTIFAMILY,
            "luxury_apartments",
            {"concierge": SpecialFeaturePricingBasis.COUNT_BASED},
        ),
        (
            BuildingType.RESTAURANT,
            "quick_service",
            {
                "outdoor_seating": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "play_area": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "digital_menu_boards": SpecialFeaturePricingBasis.COUNT_BASED,
            },
        ),
        (
            BuildingType.RESTAURANT,
            "cafe",
            {
                "outdoor_seating": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "bakery_display": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "lounge_area": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "meeting_room": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            },
        ),
        (
            BuildingType.OFFICE,
            "class_a",
            {
                "fitness_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "cafeteria": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "conference_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "green_roof": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "outdoor_terrace": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "executive_floor": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "data_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "concierge": SpecialFeaturePricingBasis.COUNT_BASED,
            },
        ),
        (
            BuildingType.OFFICE,
            "class_b",
            {
                "fitness_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "cafeteria": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "conference_room": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "surface_parking": SpecialFeaturePricingBasis.COUNT_BASED,
                "storage_space": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "security_desk": SpecialFeaturePricingBasis.COUNT_BASED,
            },
        ),
        (
            BuildingType.RETAIL,
            "shopping_center",
            {
                "covered_walkway": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "loading_dock": SpecialFeaturePricingBasis.COUNT_BASED,
                "monument_signage": SpecialFeaturePricingBasis.COUNT_BASED,
                "outdoor_seating": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "drive_thru": SpecialFeaturePricingBasis.COUNT_BASED,
                "storage_units": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            },
        ),
        (
            BuildingType.RETAIL,
            "big_box",
            {
                "loading_dock": SpecialFeaturePricingBasis.COUNT_BASED,
                "mezzanine": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "auto_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "garden_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "warehouse_racking": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "refrigerated_storage": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "curbside_pickup": SpecialFeaturePricingBasis.COUNT_BASED,
            },
        ),
        (
            BuildingType.MIXED_USE,
            "office_residential",
            {
                "amenity_deck": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "business_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "conference_facility": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            },
        ),
        (
            BuildingType.MIXED_USE,
            "hotel_retail",
            {
                "conference_center": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "restaurant": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "spa": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
                "retail_arcade": SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            },
        ),
    ),
)
def test_launch_relevant_subtypes_use_structured_non_whole_project_pricing_for_migrated_features(
    building_type,
    subtype,
    expected_bases,
):
    config = get_building_config(building_type, subtype)
    assert config is not None

    for feature_id, expected_basis in expected_bases.items():
        raw_rule = config.special_features[feature_id]
        normalized_rule = normalize_special_feature_pricing_rule(feature_id, raw_rule)

        assert normalized_rule.assumption_source == STRUCTURED_RULE_SOURCE
        assert normalized_rule.basis == expected_basis
        assert normalized_rule.basis != SpecialFeaturePricingBasis.WHOLE_PROJECT_SF


@pytest.mark.parametrize(("building_type", "subtype"), STAGE3_REMAINING_ACTIVE_SUBTYPES)
def test_stage3_remaining_active_subtypes_have_no_legacy_whole_project_sf_special_feature_rules(
    building_type,
    subtype,
):
    config = get_building_config(building_type, subtype)
    assert config is not None
    assert config.special_features

    for feature_id, raw_rule in config.special_features.items():
        normalized_rule = normalize_special_feature_pricing_rule(feature_id, raw_rule)

        assert normalized_rule.assumption_source == STRUCTURED_RULE_SOURCE
        assert normalized_rule.basis != SpecialFeaturePricingBasis.WHOLE_PROJECT_SF


@pytest.mark.parametrize(
    (
        "building_type",
        "subtype",
        "square_footage",
        "feature_id",
        "expected_basis",
        "expected_quantity",
        "expected_total_cost",
        "expected_area_share",
        "expected_cost_per_count",
    ),
    (
        (
            BuildingType.HEALTHCARE,
            "hospital",
            220_000,
            "emergency_department",
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            22_000.0,
            1_100_000.0,
            0.10,
            None,
        ),
        (
            BuildingType.EDUCATIONAL,
            "elementary_school",
            70_000,
            "playground",
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            7_000.0,
            140_000.0,
            0.10,
            None,
        ),
        (
            BuildingType.PARKING,
            "parking_garage",
            180_000,
            "ev_charging",
            SpecialFeaturePricingBasis.COUNT_BASED,
            24.0,
            288_000.0,
            None,
            12_000.0,
        ),
        (
            BuildingType.PARKING,
            "surface_parking",
            120_000,
            "valet_booth",
            SpecialFeaturePricingBasis.COUNT_BASED,
            1.0,
            75_000.0,
            None,
            75_000.0,
        ),
        (
            BuildingType.SPECIALTY,
            "data_center",
            120_000,
            "dual_fiber_meet_me_room",
            SpecialFeaturePricingBasis.COUNT_BASED,
            1.0,
            650_000.0,
            None,
            650_000.0,
        ),
        (
            BuildingType.RECREATION,
            "fitness_center",
            60_000,
            "pool",
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
            12_000.0,
            540_000.0,
            0.20,
            None,
        ),
        (
            BuildingType.CIVIC,
            "public_safety",
            45_000,
            "training_tower",
            SpecialFeaturePricingBasis.COUNT_BASED,
            1.0,
            450_000.0,
            None,
            450_000.0,
        ),
    ),
)
def test_stage3_remaining_active_example_features_use_localized_structured_pricing(
    building_type,
    subtype,
    square_footage,
    feature_id,
    expected_basis,
    expected_quantity,
    expected_total_cost,
    expected_area_share,
    expected_cost_per_count,
):
    result = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=[feature_id],
    )

    breakdown_row = _special_feature_breakdown_by_id(result)[feature_id]
    pricing_row = _available_special_feature_pricing_by_id(result)[feature_id]

    assert breakdown_row["pricing_basis"] == expected_basis.value
    assert pricing_row["pricing_basis"] == expected_basis.value
    assert breakdown_row["assumption_source"] == STRUCTURED_RULE_SOURCE
    assert pricing_row["assumption_source"] == STRUCTURED_RULE_SOURCE
    assert breakdown_row["applied_quantity"] == pytest.approx(expected_quantity)
    assert breakdown_row["total_cost"] == pytest.approx(expected_total_cost)
    assert result["construction_costs"]["special_features_total"] == pytest.approx(expected_total_cost)

    if expected_basis == SpecialFeaturePricingBasis.AREA_SHARE_GSF:
        assert breakdown_row["configured_area_share_of_gsf"] == pytest.approx(expected_area_share)
        assert pricing_row["configured_area_share_of_gsf"] == pytest.approx(expected_area_share)
        assert "configured_cost_per_count" not in breakdown_row

    if expected_basis == SpecialFeaturePricingBasis.COUNT_BASED:
        assert breakdown_row["configured_cost_per_count"] == pytest.approx(expected_cost_per_count)
        assert pricing_row["configured_cost_per_count"] == pytest.approx(expected_cost_per_count)
        assert "configured_area_share_of_gsf" not in breakdown_row


@pytest.mark.parametrize(
    (
        "building_type",
        "subtype",
        "square_footage",
        "feature_id",
        "parsed_input_overrides",
        "expected_basis",
    ),
    (
        (
            BuildingType.HOSPITALITY,
            "limited_service_hotel",
            52_000,
            "breakfast_area",
            None,
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
        ),
        (
            BuildingType.MULTIFAMILY,
            "luxury_apartments",
            64_000,
            "concierge",
            None,
            SpecialFeaturePricingBasis.COUNT_BASED,
        ),
        (
            BuildingType.RESTAURANT,
            "quick_service",
            3_200,
            "digital_menu_boards",
            None,
            SpecialFeaturePricingBasis.COUNT_BASED,
        ),
        (
            BuildingType.RESTAURANT,
            "cafe",
            3_200,
            "meeting_room",
            None,
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
        ),
        (
            BuildingType.OFFICE,
            "class_a",
            300_000,
            "executive_floor",
            None,
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
        ),
        (
            BuildingType.OFFICE,
            "class_b",
            100_000,
            "surface_parking",
            None,
            SpecialFeaturePricingBasis.COUNT_BASED,
        ),
        (
            BuildingType.RETAIL,
            "shopping_center",
            95_000,
            "drive_thru",
            None,
            SpecialFeaturePricingBasis.COUNT_BASED,
        ),
        (
            BuildingType.RETAIL,
            "big_box",
            180_000,
            "warehouse_racking",
            None,
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
        ),
        (
            BuildingType.MIXED_USE,
            "office_residential",
            125_000,
            "amenity_deck",
            None,
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
        ),
        (
            BuildingType.MIXED_USE,
            "hotel_retail",
            125_000,
            "retail_arcade",
            None,
            SpecialFeaturePricingBasis.AREA_SHARE_GSF,
        ),
    ),
)
def test_launch_relevant_engine_breakdown_uses_structured_basis_after_config_migration(
    building_type,
    subtype,
    square_footage,
    feature_id,
    parsed_input_overrides,
    expected_basis,
):
    result = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=[feature_id],
        parsed_input_overrides=parsed_input_overrides,
    )

    breakdown_row = _special_feature_breakdown_by_id(result)[feature_id]
    pricing_row = _available_special_feature_pricing_by_id(result)[feature_id]

    assert breakdown_row["pricing_basis"] == expected_basis.value
    assert pricing_row["pricing_basis"] == expected_basis.value
    assert breakdown_row["assumption_source"] == STRUCTURED_RULE_SOURCE
    assert pricing_row["assumption_source"] == STRUCTURED_RULE_SOURCE
    assert breakdown_row["pricing_basis"] != SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value

    if expected_basis == SpecialFeaturePricingBasis.AREA_SHARE_GSF:
        assert breakdown_row["configured_area_share_of_gsf"] > 0.0
        assert breakdown_row["applied_quantity"] <= square_footage
        assert "configured_cost_per_sf" not in breakdown_row
    if expected_basis == SpecialFeaturePricingBasis.COUNT_BASED:
        assert breakdown_row["configured_cost_per_count"] > 0.0
        assert pricing_row["configured_cost_per_count"] > 0.0
        assert "configured_cost_per_sf" not in breakdown_row


@pytest.mark.parametrize(
    ("pricing_status", "expected_rate", "expected_total_cost"),
    (
        (INCREMENTAL, 60.0, 60.0 * (0.04 * 85_000.0)),
        (INCLUDED_IN_BASELINE, 0.0, 0.0),
    ),
)
def test_area_share_rule_application_preserves_status_zeroing(
    pricing_status,
    expected_rate,
    expected_total_cost,
):
    rule = normalize_special_feature_pricing_rule(
        "spa",
        {
            "basis": SpecialFeaturePricingBasis.AREA_SHARE_GSF.value,
            "value": 60,
            "area_share_of_gsf": 0.04,
        },
    )

    applied = apply_special_feature_pricing_rule(
        rule=rule,
        square_footage=85_000,
        pricing_status=pricing_status,
    )

    assert applied.pricing_basis == SpecialFeaturePricingBasis.AREA_SHARE_GSF
    assert applied.configured_value == 60.0
    assert applied.applied_value == pytest.approx(expected_rate)
    assert applied.applied_quantity == pytest.approx(3_400.0)
    assert applied.configured_area_share_of_gsf == pytest.approx(0.04)
    assert applied.quantity_source == "area_share_of_gsf"
    assert applied.total_cost == pytest.approx(expected_total_cost)


def test_area_share_engine_breakdown_uses_structured_metadata_and_reconciles():
    square_footage = 85_000
    result = unified_engine.calculate_project(
        building_type=BuildingType.HOSPITALITY,
        subtype="full_service_hotel",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["ballroom", "spa"],
    )

    construction_costs = result["construction_costs"]
    breakdown_by_id = _special_feature_breakdown_by_id(result)
    ballroom_row = breakdown_by_id["ballroom"]
    spa_row = breakdown_by_id["spa"]

    assert construction_costs["special_features_total"] == pytest.approx(204000.0)

    assert ballroom_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert ballroom_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert ballroom_row["configured_value"] == pytest.approx(50.0)
    assert ballroom_row["configured_area_share_of_gsf"] == pytest.approx(0.08)
    assert ballroom_row["applied_value"] == 0.0
    assert ballroom_row["applied_quantity"] == pytest.approx(6800.0)
    assert ballroom_row["quantity_source"] == "area_share_of_gsf"
    assert ballroom_row["total_cost"] == 0.0

    assert spa_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert spa_row["pricing_status"] == INCREMENTAL
    assert spa_row["configured_value"] == pytest.approx(60.0)
    assert spa_row["configured_area_share_of_gsf"] == pytest.approx(0.04)
    assert spa_row["applied_value"] == pytest.approx(60.0)
    assert spa_row["applied_quantity"] == pytest.approx(3400.0)
    assert spa_row["quantity_source"] == "area_share_of_gsf"
    assert spa_row["total_cost"] == pytest.approx(204000.0)

    available_pricing_by_id = _available_special_feature_pricing_by_id(result)
    assert available_pricing_by_id["ballroom"]["pricing_basis"] == (
        SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    )
    assert available_pricing_by_id["ballroom"]["configured_area_share_of_gsf"] == pytest.approx(0.08)
    assert available_pricing_by_id["spa"]["pricing_basis"] == (
        SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    )
    assert available_pricing_by_id["spa"]["configured_area_share_of_gsf"] == pytest.approx(0.04)


def test_area_share_rules_use_subtype_specific_shares_for_multifamily():
    square_footage = 100_000
    market_rate = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["rooftop_amenity"],
    )
    luxury = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="luxury_apartments",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["rooftop_amenity"],
    )

    market_row = _special_feature_breakdown_by_id(market_rate)["rooftop_amenity"]
    luxury_row = _special_feature_breakdown_by_id(luxury)["rooftop_amenity"]

    assert market_row["configured_area_share_of_gsf"] == pytest.approx(0.03)
    assert market_row["applied_quantity"] == pytest.approx(3_000.0)
    assert market_row["total_cost"] == pytest.approx(72_000.0)

    assert luxury_row["configured_area_share_of_gsf"] == pytest.approx(0.05)
    assert luxury_row["applied_quantity"] == pytest.approx(5_000.0)
    assert luxury_row["total_cost"] == pytest.approx(175_000.0)

    assert market_rate["construction_costs"]["special_features_total"] == pytest.approx(72_000.0)
    assert luxury["construction_costs"]["special_features_total"] == pytest.approx(175_000.0)


@pytest.mark.parametrize(
    (
        "building_type",
        "subtype",
        "square_footage",
        "feature_id",
        "expected_value",
        "expected_share",
    ),
    (
        (
            BuildingType.MULTIFAMILY,
            "market_rate_apartments",
            250_000,
            "parking_garage",
            32.0,
            0.28,
        ),
        (
            BuildingType.MULTIFAMILY,
            "luxury_apartments",
            250_000,
            "parking_garage",
            45.0,
            0.32,
        ),
        (
            BuildingType.MULTIFAMILY,
            "affordable_housing",
            250_000,
            "parking_garage",
            26.0,
            0.22,
        ),
        (
            BuildingType.OFFICE,
            "class_a",
            300_000,
            "structured_parking",
            45.0,
            0.24,
        ),
        (
            BuildingType.MIXED_USE,
            "retail_residential",
            250_000,
            "parking_podium",
            40.0,
            0.22,
        ),
    ),
)
def test_garage_style_incremental_features_now_price_from_area_share_of_gsf(
    building_type,
    subtype,
    square_footage,
    feature_id,
    expected_value,
    expected_share,
):
    result = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Dallas, TX",
        project_class=ProjectClass.GROUND_UP,
        special_features=[feature_id],
    )

    construction_costs = result["construction_costs"]
    breakdown_row = _special_feature_breakdown_by_id(result)[feature_id]
    available_pricing_row = _available_special_feature_pricing_by_id(result)[feature_id]
    expected_quantity = square_footage * expected_share
    expected_total_cost = expected_value * expected_quantity

    assert breakdown_row["pricing_status"] == INCREMENTAL
    assert breakdown_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert breakdown_row["configured_value"] == pytest.approx(expected_value)
    assert breakdown_row["configured_area_share_of_gsf"] == pytest.approx(expected_share)
    assert breakdown_row["applied_value"] == pytest.approx(expected_value)
    assert breakdown_row["applied_quantity"] == pytest.approx(expected_quantity)
    assert breakdown_row["quantity_source"] == "area_share_of_gsf"
    assert breakdown_row["assumption_source"] == STRUCTURED_RULE_SOURCE
    assert breakdown_row["total_cost"] == pytest.approx(expected_total_cost)
    assert breakdown_row["applied_quantity"] < square_footage
    assert breakdown_row["total_cost"] < expected_value * square_footage

    assert construction_costs["special_features_total"] == pytest.approx(expected_total_cost)

    assert available_pricing_row["pricing_status"] == INCREMENTAL
    assert available_pricing_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert available_pricing_row["configured_value"] == pytest.approx(expected_value)
    assert available_pricing_row["configured_area_share_of_gsf"] == pytest.approx(expected_share)


def test_medical_office_building_tenant_improvements_allocation_composes_construction_view_trade_basis_without_double_counting():
    result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="medical_office_building",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["tenant_improvements"],
    )

    construction_costs = result["construction_costs"]
    tenant_improvements_row = _special_feature_breakdown_by_id(result)["tenant_improvements"]
    base_trade_breakdown = result["trade_breakdown"]
    construction_view_trade_breakdown = result["construction_view_trade_breakdown"]
    construction_view_scope_items = result["construction_view_scope_items"]
    tenant_improvements_total = tenant_improvements_row["total_cost"]
    expected_trade_allocation_weights = {
        "mechanical": 0.24,
        "electrical": 0.24,
        "plumbing": 0.16,
        "finishes": 0.36,
    }
    expected_trade_allocation_amounts = {
        "mechanical": 864_000.0,
        "electrical": 864_000.0,
        "plumbing": 576_000.0,
        "finishes": 1_296_000.0,
    }

    assert tenant_improvements_row["pricing_status"] == INCREMENTAL
    assert tenant_improvements_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert tenant_improvements_row["configured_area_share_of_gsf"] == pytest.approx(0.75)
    assert tenant_improvements_row["applied_quantity"] == pytest.approx(90_000.0)
    assert tenant_improvements_row["total_cost"] == pytest.approx(3_600_000.0)
    assert tenant_improvements_row["trade_composition_mode"] == "incremental_premium_with_trade_allocation"
    assert tenant_improvements_row["trade_allocation_applied"] is True
    assert tenant_improvements_row["trade_allocation_note"] == SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE
    assert tenant_improvements_row["trade_allocation_weights"] == pytest.approx(
        expected_trade_allocation_weights
    )
    assert tenant_improvements_row["trade_allocation_amounts"] == pytest.approx(
        expected_trade_allocation_amounts
    )

    assert construction_costs["special_features_total"] == pytest.approx(tenant_improvements_total)
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(
        tenant_improvements_total
    )
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"] + tenant_improvements_total
    )
    assert sum(base_trade_breakdown.values()) == pytest.approx(construction_costs["construction_total"])
    assert sum(construction_view_trade_breakdown.values()) == pytest.approx(
        construction_costs["construction_view_trade_total"]
    )
    assert construction_view_trade_breakdown["structural"] == pytest.approx(
        base_trade_breakdown["structural"]
    )

    for trade_key, allocated_amount in expected_trade_allocation_amounts.items():
        assert construction_view_trade_breakdown[trade_key] == pytest.approx(
            base_trade_breakdown[trade_key] + allocated_amount
        )
        assert construction_view_trade_breakdown[trade_key] > base_trade_breakdown[trade_key]

    allocated_scope_systems = [
        system
        for item in construction_view_scope_items
        if isinstance(item, dict)
        for system in item.get("systems", [])
        if isinstance(system, dict)
        and system.get("source") == "special_feature_trade_allocation"
        and system.get("feature_id") == "tenant_improvements"
    ]
    assert len(allocated_scope_systems) == len(expected_trade_allocation_amounts)
    assert all(
        system.get("name") == "Tenant Improvements allocated premium"
        for system in allocated_scope_systems
    )
    assert _scope_item_totals_by_trade(construction_view_scope_items) == pytest.approx(
        construction_view_trade_breakdown
    )
    assert result["totals"]["hard_costs"] == pytest.approx(
        construction_costs["construction_total"]
        + construction_costs["equipment_total"]
        + construction_costs["special_features_total"]
    )


def test_medical_office_building_without_tenant_improvements_preserves_legacy_construction_view_trade_basis():
    result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="medical_office_building",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["ambulatory_buildout"],
    )

    construction_costs = result["construction_costs"]
    ambulatory_buildout_row = _special_feature_breakdown_by_id(result)["ambulatory_buildout"]

    assert ambulatory_buildout_row["pricing_status"] == INCREMENTAL
    assert ambulatory_buildout_row["trade_composition_mode"] == "incremental_premium_only"
    assert "trade_allocation_applied" not in ambulatory_buildout_row
    assert construction_costs["special_features_total"] == pytest.approx(1_296_000.0)
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"]
    )
    assert result["construction_view_trade_breakdown"] == pytest.approx(result["trade_breakdown"])
    assert result["construction_view_scope_items"] == result["scope_items"]
    assert result["totals"]["hard_costs"] == pytest.approx(
        construction_costs["construction_total"]
        + construction_costs["equipment_total"]
        + construction_costs["special_features_total"]
    )


def test_market_rate_parking_garage_allocation_composes_construction_view_trade_basis_without_double_counting():
    result = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=250_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["parking_garage", "rooftop_amenity"],
        parsed_input_overrides={"unit_count": 220},
    )

    construction_costs = result["construction_costs"]
    breakdown_by_id = _special_feature_breakdown_by_id(result)
    parking_row = breakdown_by_id["parking_garage"]
    rooftop_row = breakdown_by_id["rooftop_amenity"]
    base_trade_breakdown = result["trade_breakdown"]
    construction_view_trade_breakdown = result["construction_view_trade_breakdown"]
    construction_view_scope_items = result["construction_view_scope_items"]
    parking_total = parking_row["total_cost"]

    assert construction_costs["construction_total"] == pytest.approx(37_337_500.0)
    assert construction_costs["equipment_total"] == pytest.approx(3_750_000.0)
    assert construction_costs["special_features_total"] == pytest.approx(2_420_000.0)
    assert result["totals"]["hard_costs"] == pytest.approx(43_507_500.0)

    assert parking_row["pricing_status"] == INCREMENTAL
    assert parking_row["trade_composition_mode"] == "incremental_premium_with_trade_allocation"
    assert parking_row["trade_allocation_applied"] is True
    assert parking_row["trade_allocation_note"] == SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE
    assert parking_row["trade_allocation_amounts"]["structural"] == pytest.approx(1_568_000.0)
    assert parking_total == pytest.approx(2_240_000.0)

    assert rooftop_row["pricing_status"] == INCREMENTAL
    assert rooftop_row["trade_composition_mode"] == "incremental_premium_only"
    assert "trade_allocation_applied" not in rooftop_row
    assert "trade_allocation_note" not in rooftop_row
    assert rooftop_row["total_cost"] == pytest.approx(180_000.0)

    assert sum(base_trade_breakdown.values()) == pytest.approx(construction_costs["construction_total"])
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(parking_total)
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"] + parking_total
    )
    assert sum(construction_view_trade_breakdown.values()) == pytest.approx(
        construction_costs["construction_view_trade_total"]
    )
    assert construction_view_trade_breakdown["structural"] == pytest.approx(12_769_250.0)
    assert construction_view_trade_breakdown["structural"] > base_trade_breakdown["structural"]
    assert result["totals"]["hard_costs"] == pytest.approx(
        construction_costs["construction_total"]
        + construction_costs["equipment_total"]
        + construction_costs["special_features_total"]
    )
    assert _scope_item_totals_by_trade(construction_view_scope_items) == pytest.approx(
        construction_view_trade_breakdown
    )


@pytest.mark.parametrize(
    ("subtype", "expected_parking_total"),
    (
        ("luxury_apartments", 3_600_000.0),
        ("affordable_housing", 1_430_000.0),
    ),
)
def test_multifamily_launch_subtype_parking_garage_allocation_spot_checks(
    subtype,
    expected_parking_total,
):
    result = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype=subtype,
        square_footage=250_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["parking_garage"],
    )

    construction_costs = result["construction_costs"]
    parking_row = _special_feature_breakdown_by_id(result)["parking_garage"]

    assert parking_row["trade_allocation_applied"] is True
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(
        expected_parking_total
    )
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"] + expected_parking_total
    )
    assert result["totals"]["hard_costs"] == pytest.approx(
        construction_costs["construction_total"]
        + construction_costs["equipment_total"]
        + construction_costs["special_features_total"]
    )
    assert sum(result["construction_view_trade_breakdown"].values()) == pytest.approx(
        construction_costs["construction_view_trade_total"]
    )


def test_class_a_structured_parking_allocation_composes_construction_view_trade_basis_without_double_counting():
    result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=300_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["structured_parking", "conference_center"],
    )

    construction_costs = result["construction_costs"]
    breakdown_by_id = _special_feature_breakdown_by_id(result)
    structured_parking_row = breakdown_by_id["structured_parking"]
    conference_center_row = breakdown_by_id["conference_center"]
    base_trade_breakdown = result["trade_breakdown"]
    construction_view_trade_breakdown = result["construction_view_trade_breakdown"]
    construction_view_scope_items = result["construction_view_scope_items"]
    structured_parking_total = structured_parking_row["total_cost"]

    assert structured_parking_row["pricing_status"] == INCREMENTAL
    assert structured_parking_row["trade_composition_mode"] == "incremental_premium_with_trade_allocation"
    assert structured_parking_row["trade_allocation_applied"] is True
    assert structured_parking_row["trade_allocation_note"] == SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE
    assert structured_parking_row["trade_allocation_amounts"]["structural"] == pytest.approx(2_268_000.0)
    assert structured_parking_total == pytest.approx(3_240_000.0)

    assert conference_center_row["pricing_status"] == INCREMENTAL
    assert conference_center_row["trade_composition_mode"] == "incremental_premium_only"
    assert "trade_allocation_applied" not in conference_center_row
    assert conference_center_row["total_cost"] == pytest.approx(360_000.0)

    assert construction_costs["special_features_total"] == pytest.approx(3_600_000.0)
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(
        structured_parking_total
    )
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"] + structured_parking_total
    )
    assert sum(base_trade_breakdown.values()) == pytest.approx(construction_costs["construction_total"])
    assert sum(construction_view_trade_breakdown.values()) == pytest.approx(
        construction_costs["construction_view_trade_total"]
    )
    assert construction_view_trade_breakdown["structural"] > base_trade_breakdown["structural"]
    assert result["totals"]["hard_costs"] == pytest.approx(
        construction_costs["construction_total"]
        + construction_costs["equipment_total"]
        + construction_costs["special_features_total"]
    )
    assert _scope_item_totals_by_trade(construction_view_scope_items) == pytest.approx(
        construction_view_trade_breakdown
    )


def test_class_a_without_structured_parking_preserves_legacy_construction_view_trade_basis():
    result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=300_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["conference_center"],
    )

    construction_costs = result["construction_costs"]
    conference_center_row = _special_feature_breakdown_by_id(result)["conference_center"]

    assert conference_center_row["trade_composition_mode"] == "incremental_premium_only"
    assert "trade_allocation_applied" not in conference_center_row
    assert construction_costs["special_features_total"] == pytest.approx(360_000.0)
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"]
    )
    assert result["construction_view_trade_breakdown"] == pytest.approx(result["trade_breakdown"])
    assert result["construction_view_scope_items"] == result["scope_items"]


def test_mixed_use_parking_podium_allocation_composes_construction_view_trade_basis_without_double_counting():
    result = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="retail_residential",
        square_footage=250_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["parking_podium"],
    )

    construction_costs = result["construction_costs"]
    parking_podium_row = _special_feature_breakdown_by_id(result)["parking_podium"]
    base_trade_breakdown = result["trade_breakdown"]
    construction_view_trade_breakdown = result["construction_view_trade_breakdown"]
    construction_view_scope_items = result["construction_view_scope_items"]
    parking_podium_total = parking_podium_row["total_cost"]

    assert parking_podium_row["pricing_status"] == INCREMENTAL
    assert parking_podium_row["trade_composition_mode"] == "incremental_premium_with_trade_allocation"
    assert parking_podium_row["trade_allocation_applied"] is True
    assert parking_podium_row["trade_allocation_note"] == SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE
    assert parking_podium_row["trade_allocation_amounts"]["structural"] == pytest.approx(1_540_000.0)
    assert parking_podium_total == pytest.approx(2_200_000.0)

    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(
        parking_podium_total
    )
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"] + parking_podium_total
    )
    assert sum(base_trade_breakdown.values()) == pytest.approx(construction_costs["construction_total"])
    assert sum(construction_view_trade_breakdown.values()) == pytest.approx(
        construction_costs["construction_view_trade_total"]
    )
    assert construction_view_trade_breakdown["structural"] > base_trade_breakdown["structural"]
    assert result["totals"]["hard_costs"] == pytest.approx(
        construction_costs["construction_total"]
        + construction_costs["equipment_total"]
        + construction_costs["special_features_total"]
    )
    assert _scope_item_totals_by_trade(construction_view_scope_items) == pytest.approx(
        construction_view_trade_breakdown
    )


def test_mixed_use_without_parking_podium_preserves_legacy_construction_view_trade_basis():
    result = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="retail_residential",
        square_footage=250_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["rooftop_deck"],
    )

    construction_costs = result["construction_costs"]
    rooftop_row = _special_feature_breakdown_by_id(result)["rooftop_deck"]

    assert rooftop_row["trade_composition_mode"] == "included_in_baseline"
    assert "trade_allocation_applied" not in rooftop_row
    assert construction_costs["special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"]
    )
    assert result["construction_view_trade_breakdown"] == pytest.approx(result["trade_breakdown"])
    assert result["construction_view_scope_items"] == result["scope_items"]


def test_non_allocated_incremental_features_preserve_prior_trade_basis_behavior():
    result = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=100_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["rooftop_amenity"],
    )

    construction_costs = result["construction_costs"]
    rooftop_row = _special_feature_breakdown_by_id(result)["rooftop_amenity"]

    assert rooftop_row["trade_composition_mode"] == "incremental_premium_only"
    assert "trade_allocation_applied" not in rooftop_row
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"]
    )
    assert result["construction_view_trade_breakdown"] == pytest.approx(result["trade_breakdown"])
    assert result["construction_view_scope_items"] == result["scope_items"]


def test_included_in_baseline_features_remain_zero_cost_and_do_not_allocate_without_metadata():
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=8_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["valet_parking"],
    )

    construction_costs = result["construction_costs"]
    valet_row = _special_feature_breakdown_by_id(result)["valet_parking"]

    assert valet_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert valet_row["trade_composition_mode"] == "included_in_baseline"
    assert valet_row["total_cost"] == pytest.approx(0.0)
    assert "trade_allocation_applied" not in valet_row
    assert construction_costs["special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_allocated_special_features_total"] == pytest.approx(0.0)
    assert construction_costs["construction_view_trade_total"] == pytest.approx(
        construction_costs["construction_total"]
    )
    assert result["construction_view_trade_breakdown"] == pytest.approx(result["trade_breakdown"])


def test_area_share_industrial_zones_reconcile_with_included_and_incremental_statuses():
    square_footage = 220_000
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="distribution_center",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["office_buildout", "refrigerated_area"],
    )

    breakdown_by_id = _special_feature_breakdown_by_id(result)
    office_row = breakdown_by_id["office_buildout"]
    refrigerated_row = breakdown_by_id["refrigerated_area"]

    assert result["construction_costs"]["special_features_total"] == pytest.approx(924_000.0)

    assert office_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert office_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert office_row["configured_area_share_of_gsf"] == pytest.approx(0.05)
    assert office_row["applied_quantity"] == pytest.approx(11_000.0)
    assert office_row["applied_value"] == 0.0
    assert office_row["total_cost"] == 0.0

    assert refrigerated_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert refrigerated_row["pricing_status"] == INCREMENTAL
    assert refrigerated_row["configured_area_share_of_gsf"] == pytest.approx(0.12)
    assert refrigerated_row["applied_quantity"] == pytest.approx(26_400.0)
    assert refrigerated_row["applied_value"] == pytest.approx(35.0)
    assert refrigerated_row["total_cost"] == pytest.approx(924_000.0)


def test_structured_whole_project_sf_rules_flow_through_engine_without_repricing(monkeypatch):
    square_footage = 48_000
    config = get_building_config(BuildingType.RETAIL, "shopping_center")
    assert config is not None

    monkeypatch.setattr(
        config,
        "special_features",
        {
            "covered_walkway": {
                "basis": SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value,
                "value": 20,
            },
            "drive_thru": {
                "basis": SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value,
                "value": 40,
            },
        },
    )

    result = unified_engine.calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["covered_walkway", "drive_thru"],
    )

    construction_costs = result["construction_costs"]
    assert construction_costs["special_features_total"] == pytest.approx(40.0 * square_footage)

    breakdown_by_id = {
        row["id"]: row
        for row in construction_costs["special_features_breakdown"]
        if isinstance(row, dict) and row.get("id")
    }
    included_row = breakdown_by_id["covered_walkway"]
    incremental_row = breakdown_by_id["drive_thru"]

    assert included_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert included_row["pricing_basis"] == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value
    assert included_row["configured_value"] == pytest.approx(20.0)
    assert included_row["configured_cost_per_sf"] == pytest.approx(20.0)
    assert included_row["cost_per_sf"] == 0.0
    assert included_row["total_cost"] == 0.0
    assert included_row["assumption_source"] == STRUCTURED_RULE_SOURCE

    assert incremental_row["pricing_status"] == INCREMENTAL
    assert incremental_row["pricing_basis"] == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value
    assert incremental_row["configured_value"] == pytest.approx(40.0)
    assert incremental_row["configured_cost_per_sf"] == pytest.approx(40.0)
    assert incremental_row["cost_per_sf"] == pytest.approx(40.0)
    assert incremental_row["applied_quantity"] == pytest.approx(square_footage)
    assert incremental_row["total_cost"] == pytest.approx(40.0 * square_footage)
    assert incremental_row["assumption_source"] == STRUCTURED_RULE_SOURCE

    available_pricing_by_id = {
        row["id"]: row
        for row in result["project_info"]["available_special_feature_pricing"]
        if isinstance(row, dict) and row.get("id")
    }
    assert available_pricing_by_id["covered_walkway"]["pricing_basis"] == (
        SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value
    )
    assert available_pricing_by_id["covered_walkway"]["configured_value"] == pytest.approx(20.0)
    assert available_pricing_by_id["covered_walkway"]["configured_cost_per_sf"] == pytest.approx(20.0)
    assert available_pricing_by_id["covered_walkway"]["assumption_source"] == STRUCTURED_RULE_SOURCE
    assert available_pricing_by_id["drive_thru"]["pricing_basis"] == (
        SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value
    )
    assert available_pricing_by_id["drive_thru"]["configured_value"] == pytest.approx(40.0)


def test_operating_room_count_override_bills_only_overage_above_included_baseline():
    result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="surgical_center",
        square_footage=18_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["operating_room"],
        parsed_input_overrides={"operating_room_count": 5},
    )

    operating_room_row = _special_feature_breakdown_by_id(result)["operating_room"]

    assert result["construction_costs"]["special_features_total"] == pytest.approx(450000.0)
    assert operating_room_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert operating_room_row["count_pricing_mode"] == "overage_above_default"
    assert operating_room_row["configured_cost_per_count"] == pytest.approx(450000.0)
    assert operating_room_row["cost_per_count"] == pytest.approx(450000.0)
    assert operating_room_row["applied_quantity"] == pytest.approx(1.0)
    assert operating_room_row["quantity_source"] == "overage_above_default"
    assert operating_room_row["requested_quantity"] == pytest.approx(5.0)
    assert operating_room_row["requested_quantity_source"] == "explicit_override:operating_room_count"
    assert operating_room_row["included_baseline_quantity"] == pytest.approx(4.0)
    assert operating_room_row["included_baseline_quantity_source"] == "size_band_default"
    assert operating_room_row["billed_quantity"] == pytest.approx(1.0)
    assert operating_room_row["billed_quantity_source"] == "overage_above_default"
    assert operating_room_row["resolved_size_band"] == "mid_asc"
    assert operating_room_row["unit_label"] == "room"
    assert operating_room_row["total_cost"] == pytest.approx(450000.0)


def test_operatory_count_override_bills_only_overage_above_included_baseline():
    result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="dental_office",
        square_footage=4_500,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["operatory"],
        parsed_input_overrides={"operatory_count": 9},
    )

    operatory_row = _special_feature_breakdown_by_id(result)["operatory"]

    assert result["construction_costs"]["special_features_total"] == pytest.approx(45000.0)
    assert operatory_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert operatory_row["count_pricing_mode"] == "overage_above_default"
    assert operatory_row["configured_cost_per_count"] == pytest.approx(45000.0)
    assert operatory_row["cost_per_count"] == pytest.approx(45000.0)
    assert operatory_row["applied_quantity"] == pytest.approx(1.0)
    assert operatory_row["quantity_source"] == "overage_above_default"
    assert operatory_row["requested_quantity"] == pytest.approx(9.0)
    assert operatory_row["requested_quantity_source"] == "explicit_override:operatory_count"
    assert operatory_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert operatory_row["included_baseline_quantity_source"] == "size_band_default"
    assert operatory_row["billed_quantity"] == pytest.approx(1.0)
    assert operatory_row["billed_quantity_source"] == "overage_above_default"
    assert operatory_row["resolved_size_band"] == "large_practice"
    assert operatory_row["unit_label"] == "operatory"
    assert operatory_row["total_cost"] == pytest.approx(45000.0)


def test_mri_suite_count_override_bills_only_overage_above_included_baseline():
    result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="imaging_center",
        square_footage=12_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["mri_suite"],
        parsed_input_overrides={"mri_suite_count": 2},
    )

    mri_row = _special_feature_breakdown_by_id(result)["mri_suite"]

    assert result["construction_costs"]["special_features_total"] == pytest.approx(850000.0)
    assert mri_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert mri_row["count_pricing_mode"] == "overage_above_default"
    assert mri_row["configured_cost_per_count"] == pytest.approx(850000.0)
    assert mri_row["cost_per_count"] == pytest.approx(850000.0)
    assert mri_row["applied_quantity"] == pytest.approx(1.0)
    assert mri_row["quantity_source"] == "overage_above_default"
    assert mri_row["requested_quantity"] == pytest.approx(2.0)
    assert mri_row["requested_quantity_source"] == "explicit_override:mri_suite_count"
    assert mri_row["included_baseline_quantity"] == pytest.approx(1.0)
    assert mri_row["included_baseline_quantity_source"] == "configured_default_count"
    assert mri_row["billed_quantity"] == pytest.approx(1.0)
    assert mri_row["billed_quantity_source"] == "overage_above_default"
    assert mri_row["unit_label"] == "suite"
    assert mri_row["total_cost"] == pytest.approx(850000.0)


@pytest.mark.parametrize(
    (
        "building_type",
        "subtype",
        "square_footage",
        "feature_id",
        "parsed_input_overrides",
        "expected_baseline_quantity",
        "expected_baseline_source",
    ),
    (
        (
            BuildingType.HEALTHCARE,
            "surgical_center",
            18_000,
            "operating_room",
            {"operating_room_count": 4},
            4.0,
            "size_band_default",
        ),
        (
            BuildingType.HEALTHCARE,
            "imaging_center",
            12_000,
            "mri_suite",
            {"mri_suite_count": 1},
            1.0,
            "configured_default_count",
        ),
        (
            BuildingType.INDUSTRIAL,
            "distribution_center",
            220_000,
            "extra_loading_docks",
            {"loading_dock_count": 8},
            8.0,
            "size_band_default",
        ),
        (
            BuildingType.INDUSTRIAL,
            "warehouse",
            220_000,
            "loading_docks",
            {"loading_dock_count": 8},
            8.0,
            "size_band_default",
        ),
    ),
)
def test_overage_mode_features_bill_zero_when_requested_count_does_not_exceed_baseline(
    building_type,
    subtype,
    square_footage,
    feature_id,
    parsed_input_overrides,
    expected_baseline_quantity,
    expected_baseline_source,
):
    result = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=[feature_id],
        parsed_input_overrides=parsed_input_overrides,
    )

    row = _special_feature_breakdown_by_id(result)[feature_id]

    requested_count = next(iter(parsed_input_overrides.values()))
    assert result["construction_costs"]["special_features_total"] == 0.0
    assert row["count_pricing_mode"] == "overage_above_default"
    assert row["cost_per_count"] == 0.0
    assert row["applied_quantity"] == 0.0
    assert row["quantity_source"] == "overage_above_default"
    assert row["requested_quantity"] == pytest.approx(float(requested_count))
    assert row["included_baseline_quantity"] == pytest.approx(expected_baseline_quantity)
    assert row["included_baseline_quantity_source"] == expected_baseline_source
    assert row["billed_quantity"] == 0.0
    assert row["billed_quantity_source"] == "overage_above_default"
    assert row["total_cost"] == 0.0


@pytest.mark.parametrize(
    (
        "building_type",
        "subtype",
        "square_footage",
        "feature_id",
        "parsed_input_overrides",
        "expected_total_cost",
        "expected_quantity_source",
        "expected_applied_quantity",
        "expected_unit_label",
        "expected_count_pricing_mode",
        "expected_included_baseline_quantity",
    ),
    (
        (
            BuildingType.RESTAURANT,
            "cafe",
            3_200,
            "drive_thru",
            {"drive_thru_lane_count": 2},
            150000.0,
            "explicit_override:drive_thru_lane_count",
            2.0,
            "lane",
            "all_units",
            None,
        ),
        (
            BuildingType.INDUSTRIAL,
            "distribution_center",
            220_000,
            "extra_loading_docks",
            {"loading_dock_count": 10},
            130000.0,
            "overage_above_default",
            2.0,
            "dock",
            "overage_above_default",
            8.0,
        ),
        (
            BuildingType.INDUSTRIAL,
            "warehouse",
            220_000,
            "loading_docks",
            {"loading_dock_count": 10},
            130000.0,
            "overage_above_default",
            2.0,
            "dock",
            "overage_above_default",
            8.0,
        ),
        (
            BuildingType.INDUSTRIAL,
            "flex_space",
            80_000,
            "crane_bays",
            {"crane_bay_count": 3},
            750000.0,
            "explicit_override:crane_bay_count",
            3.0,
            "bay",
            "all_units",
            None,
        ),
        (
            BuildingType.SPECIALTY,
            "car_dealership",
            40_000,
            "expanded_service_bays",
            {"service_bay_count": 10},
            190000.0,
            "overage_above_default",
            2.0,
            "bay",
            "overage_above_default",
            8.0,
        ),
        (
            BuildingType.INDUSTRIAL,
            "manufacturing",
            100_000,
            "crane_bays",
            {"crane_bay_count": 3},
            300000.0,
            "overage_above_default",
            1.0,
            "bay",
            "overage_above_default",
            2.0,
        ),
    ),
)
def test_count_based_features_apply_explicit_quantities_according_to_configured_mode(
    building_type,
    subtype,
    square_footage,
    feature_id,
    parsed_input_overrides,
    expected_total_cost,
    expected_quantity_source,
    expected_applied_quantity,
    expected_unit_label,
    expected_count_pricing_mode,
    expected_included_baseline_quantity,
):
    result = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=[feature_id],
        parsed_input_overrides=parsed_input_overrides,
    )

    row = _special_feature_breakdown_by_id(result)[feature_id]

    assert row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert row["count_pricing_mode"] == expected_count_pricing_mode
    assert row["quantity_source"] == expected_quantity_source
    assert row["applied_quantity"] == pytest.approx(expected_applied_quantity)
    assert row["requested_quantity"] == pytest.approx(
        float(next(iter(parsed_input_overrides.values())))
    )
    assert row["unit_label"] == expected_unit_label
    assert row["total_cost"] == pytest.approx(expected_total_cost)
    if expected_included_baseline_quantity is None:
        assert "included_baseline_quantity" not in row
    else:
        assert row["included_baseline_quantity"] == pytest.approx(
            expected_included_baseline_quantity
        )
    assert result["construction_costs"]["special_features_total"] == pytest.approx(expected_total_cost)


@pytest.mark.parametrize(
    ("square_footage", "expected_quantity", "expected_band"),
    (
        (10_000, 2.0, "small_asc"),
        (18_000, 4.0, "mid_asc"),
        (24_000, 6.0, "large_asc"),
    ),
)
def test_operating_room_defaults_use_deterministic_size_bands(square_footage, expected_quantity, expected_band):
    result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="surgical_center",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["operating_room"],
    )

    row = _special_feature_breakdown_by_id(result)["operating_room"]

    assert row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert row["count_pricing_mode"] == "overage_above_default"
    assert row["applied_quantity"] == pytest.approx(expected_quantity)
    assert row["quantity_source"] == "size_band_default"
    assert row["requested_quantity"] == pytest.approx(expected_quantity)
    assert row["included_baseline_quantity"] == pytest.approx(expected_quantity)
    assert row["billed_quantity"] == pytest.approx(expected_quantity)
    assert row["resolved_size_band"] == expected_band
    assert row["total_cost"] == 0.0


def test_overage_mode_incremental_features_preserve_safe_default_behavior_without_explicit_count():
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="distribution_center",
        square_footage=220_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["extra_loading_docks"],
    )

    row = _special_feature_breakdown_by_id(result)["extra_loading_docks"]

    assert row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert row["count_pricing_mode"] == "overage_above_default"
    assert row["requested_quantity"] == pytest.approx(8.0)
    assert row["included_baseline_quantity"] == pytest.approx(8.0)
    assert row["billed_quantity"] == pytest.approx(8.0)
    assert row["quantity_source"] == "size_band_default"
    assert row["cost_per_count"] == pytest.approx(65000.0)
    assert row["applied_quantity"] == pytest.approx(8.0)
    assert row["total_cost"] == pytest.approx(520000.0)
    assert result["construction_costs"]["special_features_total"] == pytest.approx(520000.0)


def test_warehouse_launch_feature_set_surfaces_baseline_docks_and_office_buildout_honestly():
    config = get_building_config(BuildingType.INDUSTRIAL, "warehouse")

    assert config.special_features == {
        "loading_docks": {
            "basis": "COUNT_BASED",
            "value": 65000,
            "count_pricing_mode": "overage_above_default",
            "count_override_keys": [
                "extra_loading_dock_count",
                "extra_dock_count",
                "loading_dock_count",
                "dock_door_count",
                "dock_count",
            ],
            "default_count_bands": [
                {"label": "mid_box", "max_square_footage": 150000, "count": 4},
                {"label": "regional", "max_square_footage": 300000, "count": 8},
                {"label": "large_box", "max_square_footage": 600000, "count": 12},
                {"label": "mega_box", "count": 16},
            ],
            "unit_label": "dock",
        },
        "office_buildout": {
            "basis": "AREA_SHARE_GSF",
            "value": 18,
            "area_share_of_gsf": 0.05,
        },
    }
    assert config.special_feature_pricing_statuses == {
        "loading_docks": INCLUDED_IN_BASELINE,
        "office_buildout": INCLUDED_IN_BASELINE,
    }


def test_warehouse_baseline_features_render_as_included_without_incremental_premium_math():
    square_footage = 220_000
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="warehouse",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["loading_docks", "office_buildout"],
    )

    breakdown_by_id = _special_feature_breakdown_by_id(result)
    available_pricing_by_id = _available_special_feature_pricing_by_id(result)
    loading_docks_row = breakdown_by_id["loading_docks"]
    office_buildout_row = breakdown_by_id["office_buildout"]

    assert result["construction_costs"]["special_features_total"] == pytest.approx(0.0)

    assert loading_docks_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert loading_docks_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert loading_docks_row["count_pricing_mode"] == "overage_above_default"
    assert loading_docks_row["configured_value"] == pytest.approx(65000.0)
    assert loading_docks_row["configured_cost_per_count"] == pytest.approx(65000.0)
    assert loading_docks_row["cost_per_count"] == 0.0
    assert loading_docks_row["requested_quantity"] == pytest.approx(8.0)
    assert loading_docks_row["requested_quantity_source"] == "size_band_default"
    assert loading_docks_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert loading_docks_row["billed_quantity"] == pytest.approx(8.0)
    assert loading_docks_row["applied_quantity"] == pytest.approx(8.0)
    assert loading_docks_row["total_cost"] == 0.0

    assert office_buildout_row["pricing_basis"] == SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    assert office_buildout_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert office_buildout_row["configured_value"] == pytest.approx(18.0)
    assert office_buildout_row["configured_area_share_of_gsf"] == pytest.approx(0.05)
    assert office_buildout_row["applied_quantity"] == pytest.approx(square_footage * 0.05)
    assert office_buildout_row["applied_value"] == 0.0
    assert office_buildout_row["total_cost"] == 0.0

    assert available_pricing_by_id["loading_docks"]["pricing_status"] == INCLUDED_IN_BASELINE
    assert available_pricing_by_id["loading_docks"]["pricing_basis"] == (
        SpecialFeaturePricingBasis.COUNT_BASED.value
    )
    assert available_pricing_by_id["loading_docks"]["count_pricing_mode"] == "overage_above_default"
    assert available_pricing_by_id["loading_docks"]["requested_quantity"] == pytest.approx(8.0)
    assert available_pricing_by_id["loading_docks"]["included_baseline_quantity"] == pytest.approx(
        8.0
    )
    assert available_pricing_by_id["office_buildout"]["pricing_status"] == INCLUDED_IN_BASELINE
    assert available_pricing_by_id["office_buildout"]["pricing_basis"] == (
        SpecialFeaturePricingBasis.AREA_SHARE_GSF.value
    )


def test_warehouse_loading_docks_apply_overage_through_the_canonical_feature_id():
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="warehouse",
        square_footage=220_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["loading_docks"],
        parsed_input_overrides={"loading_dock_count": 10},
    )

    breakdown_by_id = _special_feature_breakdown_by_id(result)
    available_pricing_by_id = _available_special_feature_pricing_by_id(result)
    loading_docks_row = breakdown_by_id["loading_docks"]

    assert sorted(breakdown_by_id) == ["loading_docks"]
    assert sorted(available_pricing_by_id) == ["loading_docks", "office_buildout"]
    assert result["construction_costs"]["special_features_total"] == pytest.approx(130000.0)
    assert loading_docks_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert loading_docks_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert loading_docks_row["count_pricing_mode"] == "overage_above_default"
    assert loading_docks_row["requested_quantity"] == pytest.approx(10.0)
    assert loading_docks_row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert loading_docks_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert loading_docks_row["billed_quantity"] == pytest.approx(2.0)
    assert loading_docks_row["applied_quantity"] == pytest.approx(2.0)
    assert loading_docks_row["unit_label"] == "dock"
    assert loading_docks_row["total_cost"] == pytest.approx(130000.0)
    assert "extra_loading_docks" not in breakdown_by_id
    assert "extra_loading_docks" not in available_pricing_by_id


def test_cafe_drive_thru_uses_configured_default_count_and_no_longer_scales_with_square_footage():
    compact = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="cafe",
        square_footage=2_400,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["drive_thru"],
    )
    expanded = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="cafe",
        square_footage=4_800,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["drive_thru"],
    )

    compact_row = _special_feature_breakdown_by_id(compact)["drive_thru"]
    expanded_row = _special_feature_breakdown_by_id(expanded)["drive_thru"]

    assert compact_row["quantity_source"] == "configured_default_count"
    assert compact_row["applied_quantity"] == pytest.approx(1.0)
    assert compact_row["total_cost"] == pytest.approx(75000.0)
    assert expanded_row["quantity_source"] == "configured_default_count"
    assert expanded_row["applied_quantity"] == pytest.approx(1.0)
    assert expanded_row["total_cost"] == pytest.approx(75000.0)
    assert compact["construction_costs"]["special_features_total"] == pytest.approx(75000.0)
    assert expanded["construction_costs"]["special_features_total"] == pytest.approx(75000.0)


def test_quick_service_double_drive_thru_uses_two_lane_default_count():
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="quick_service",
        square_footage=3_200,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["double_drive_thru"],
    )

    row = _special_feature_breakdown_by_id(result)["double_drive_thru"]

    assert row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert row["configured_cost_per_count"] == pytest.approx(80000.0)
    assert row["applied_quantity"] == pytest.approx(2.0)
    assert row["quantity_source"] == "configured_default_count"
    assert row["unit_label"] == "lane"
    assert row["total_cost"] == pytest.approx(160000.0)


def test_available_special_feature_pricing_exposes_count_based_metadata_for_migrated_feature():
    result = unified_engine.calculate_project(
        building_type=BuildingType.SPECIALTY,
        subtype="car_dealership",
        square_footage=40_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["expanded_service_bays"],
    )

    pricing_row = _available_special_feature_pricing_by_id(result)["expanded_service_bays"]

    assert pricing_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert pricing_row["configured_value"] == pytest.approx(95000.0)
    assert pricing_row["configured_cost_per_count"] == pytest.approx(95000.0)
    assert pricing_row["count_pricing_mode"] == "overage_above_default"
    assert pricing_row["unit_label"] == "bay"
    assert pricing_row["count_override_keys"] == [
        "expanded_service_bay_count",
        "service_bay_count",
        "bay_count",
    ]


def test_available_special_feature_pricing_exposes_overage_preview_quantities_for_explicit_counts():
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="distribution_center",
        square_footage=220_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["extra_loading_docks"],
        parsed_input_overrides={"loading_dock_count": 10},
    )

    pricing_row = _available_special_feature_pricing_by_id(result)["extra_loading_docks"]

    assert pricing_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert pricing_row["count_pricing_mode"] == "overage_above_default"
    assert pricing_row["requested_quantity"] == pytest.approx(10.0)
    assert pricing_row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert pricing_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert pricing_row["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_row["billed_quantity"] == pytest.approx(2.0)
    assert pricing_row["billed_quantity_source"] == "overage_above_default"


def test_warehouse_available_special_feature_pricing_uses_loading_docks_for_explicit_overage_preview():
    result = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="warehouse",
        square_footage=220_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["loading_docks"],
        parsed_input_overrides={"loading_dock_count": 10},
    )

    pricing_by_id = _available_special_feature_pricing_by_id(result)
    pricing_row = pricing_by_id["loading_docks"]

    assert sorted(pricing_by_id) == ["loading_docks", "office_buildout"]
    assert pricing_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert pricing_row["pricing_status"] == INCLUDED_IN_BASELINE
    assert pricing_row["count_pricing_mode"] == "overage_above_default"
    assert pricing_row["requested_quantity"] == pytest.approx(10.0)
    assert pricing_row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert pricing_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert pricing_row["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_row["billed_quantity"] == pytest.approx(2.0)
    assert pricing_row["billed_quantity_source"] == "overage_above_default"
    assert "extra_loading_docks" not in pricing_by_id
