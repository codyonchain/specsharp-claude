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


def test_legacy_float_engine_breakdown_uses_normalized_whole_project_sf_metadata():
    square_footage = 64_000
    result = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["pool"],
    )

    construction_costs = result["construction_costs"]
    breakdown = construction_costs["special_features_breakdown"]
    breakdown_by_id = {
        row["id"]: row
        for row in breakdown
        if isinstance(row, dict) and row.get("id")
    }
    pool_row = breakdown_by_id["pool"]

    assert construction_costs["special_features_total"] == pytest.approx(18.0 * square_footage)
    assert pool_row["pricing_basis"] == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF.value
    assert pool_row["configured_value"] == pytest.approx(18.0)
    assert pool_row["applied_value"] == pytest.approx(18.0)
    assert pool_row["applied_quantity"] == pytest.approx(square_footage)
    assert pool_row["configured_cost_per_sf"] == pytest.approx(18.0)
    assert pool_row["cost_per_sf"] == pytest.approx(18.0)
    assert pool_row["assumption_source"] == LEGACY_FLOAT_NORMALIZATION_SOURCE
    assert pool_row["total_cost"] == pytest.approx(18.0 * square_footage)
    assert sum(
        float(item.get("total_cost", 0.0) or 0.0)
        for item in breakdown
        if isinstance(item, dict)
    ) == pytest.approx(construction_costs["special_features_total"])


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


def test_operating_room_count_override_wins_and_included_status_keeps_total_zero():
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

    assert result["construction_costs"]["special_features_total"] == 0.0
    assert operating_room_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert operating_room_row["configured_cost_per_count"] == pytest.approx(450000.0)
    assert operating_room_row["cost_per_count"] == 0.0
    assert operating_room_row["applied_quantity"] == pytest.approx(5.0)
    assert operating_room_row["quantity_source"] == "explicit_override:operating_room_count"
    assert operating_room_row["unit_label"] == "room"
    assert operating_room_row["total_cost"] == 0.0


def test_operatory_count_override_wins_and_included_status_keeps_total_zero():
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

    assert result["construction_costs"]["special_features_total"] == 0.0
    assert operatory_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert operatory_row["configured_cost_per_count"] == pytest.approx(45000.0)
    assert operatory_row["cost_per_count"] == 0.0
    assert operatory_row["applied_quantity"] == pytest.approx(9.0)
    assert operatory_row["quantity_source"] == "explicit_override:operatory_count"
    assert operatory_row["unit_label"] == "operatory"


def test_mri_suite_count_override_wins_and_included_status_keeps_total_zero():
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

    assert result["construction_costs"]["special_features_total"] == 0.0
    assert mri_row["pricing_basis"] == SpecialFeaturePricingBasis.COUNT_BASED.value
    assert mri_row["configured_cost_per_count"] == pytest.approx(850000.0)
    assert mri_row["cost_per_count"] == 0.0
    assert mri_row["applied_quantity"] == pytest.approx(2.0)
    assert mri_row["quantity_source"] == "explicit_override:mri_suite_count"
    assert mri_row["unit_label"] == "suite"


@pytest.mark.parametrize(
    (
        "building_type",
        "subtype",
        "square_footage",
        "feature_id",
        "parsed_input_overrides",
        "expected_total_cost",
        "expected_quantity_source",
        "expected_unit_label",
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
            "lane",
        ),
        (
            BuildingType.INDUSTRIAL,
            "distribution_center",
            220_000,
            "extra_loading_docks",
            {"loading_dock_count": 10},
            650000.0,
            "explicit_override:loading_dock_count",
            "dock",
        ),
        (
            BuildingType.INDUSTRIAL,
            "flex_space",
            80_000,
            "crane_bays",
            {"crane_bay_count": 3},
            750000.0,
            "explicit_override:crane_bay_count",
            "bay",
        ),
        (
            BuildingType.SPECIALTY,
            "car_dealership",
            40_000,
            "expanded_service_bays",
            {"service_bay_count": 7},
            665000.0,
            "explicit_override:service_bay_count",
            "bay",
        ),
    ),
)
def test_incremental_count_based_features_use_explicit_overrides(
    building_type,
    subtype,
    square_footage,
    feature_id,
    parsed_input_overrides,
    expected_total_cost,
    expected_quantity_source,
    expected_unit_label,
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
    assert row["quantity_source"] == expected_quantity_source
    assert row["unit_label"] == expected_unit_label
    assert row["total_cost"] == pytest.approx(expected_total_cost)
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
    assert row["applied_quantity"] == pytest.approx(expected_quantity)
    assert row["quantity_source"] == "size_band_default"
    assert row["resolved_size_band"] == expected_band
    assert row["total_cost"] == 0.0


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
    assert pricing_row["unit_label"] == "bay"
    assert pricing_row["count_override_keys"] == [
        "expanded_service_bay_count",
        "service_bay_count",
        "bay_count",
    ]
