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
