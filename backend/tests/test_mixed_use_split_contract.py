import pytest

from app.core.building_taxonomy import validate_building_type
from app.v2.config.master_config import BuildingType, ProjectClass
from app.v2.engines.unified_engine import unified_engine


def test_mixed_use_taxonomy_validation_preserves_canonical_type_and_subtype():
    building_type, subtype = validate_building_type("mixed_use", "retail_residential")
    assert building_type == "mixed_use"
    assert subtype == "retail_residential"


def test_user_input_single_component_infers_counterpart_deterministically():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="office_residential",
        square_footage=125_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {"components": {"office": 70.0}},
            "description": "mixed-use office residential project",
        },
    )

    split = payload.get("mixed_use_split")
    assert isinstance(split, dict)
    assert split.get("source") == "user_input"
    assert split.get("normalization_applied") is True
    assert split.get("inference_applied") is True
    value = split.get("value")
    assert isinstance(value, dict)
    assert value.get("office") == pytest.approx(70.0)
    assert value.get("residential") == pytest.approx(30.0)


def test_description_split_patterns_are_detected_and_normalized():
    ratio_payload = unified_engine.estimate_from_description(
        description="New 160000 sf mixed-use office and residential tower with a 60/40 split in Nashville, TN",
        square_footage=160_000,
        location="Nashville, TN",
    )
    ratio_split = ratio_payload.get("mixed_use_split")
    assert isinstance(ratio_split, dict)
    assert ratio_split.get("source") == "nlp_detected"
    assert ratio_split.get("pattern") == "ratio_pair"
    assert ratio_split.get("value", {}).get("office") == pytest.approx(60.0)
    assert ratio_split.get("value", {}).get("residential") == pytest.approx(40.0)

    percent_payload = unified_engine.estimate_from_description(
        description="New 150000 sf mixed-use office and residential project with 70% office / 30% residential in Nashville, TN",
        square_footage=150_000,
        location="Nashville, TN",
    )
    percent_split = percent_payload.get("mixed_use_split")
    assert isinstance(percent_split, dict)
    assert percent_split.get("source") == "nlp_detected"
    assert percent_split.get("pattern") == "component_percent"
    assert percent_split.get("value", {}).get("office") == pytest.approx(70.0)
    assert percent_split.get("value", {}).get("residential") == pytest.approx(30.0)


@pytest.mark.parametrize(
    "description,expected_source_component,expected_counterpart_component,expected_pattern",
    [
        (
            "New 170000 sf mixed-use retail and residential project that is mostly residential in Nashville, TN",
            "residential",
            "retail",
            "mostly_component",
        ),
        (
            "New 170000 sf mixed-use retail and residential project with a retail-heavy program in Nashville, TN",
            "retail",
            "residential",
            "heavy_component",
        ),
        (
            "New 170000 sf mixed-use office and residential project with a balanced program in Nashville, TN",
            "office",
            "residential",
            "balanced_pair",
        ),
    ],
)
def test_qualitative_split_patterns_map_to_canonical_components(
    description,
    expected_source_component,
    expected_counterpart_component,
    expected_pattern,
):
    payload = unified_engine.estimate_from_description(
        description=description,
        square_footage=170_000,
        location="Nashville, TN",
    )
    split = payload.get("mixed_use_split")
    assert isinstance(split, dict)
    assert split.get("source") == "nlp_detected"
    assert split.get("pattern") == expected_pattern
    value = split.get("value")
    assert isinstance(value, dict)
    assert value.get(expected_source_component) >= 50.0
    assert value.get(expected_counterpart_component) > 0.0
    assert sum(float(value.get(component, 0.0) or 0.0) for component in ("office", "residential", "retail", "hotel", "transit")) == pytest.approx(100.0)


def test_invalid_mix_is_explicit_and_falls_back_to_default():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="urban_mixed",
        square_footage=110_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {"components": {"unknown_component": 100.0}},
            "description": "mixed-use urban project",
        },
    )

    split = payload.get("mixed_use_split")
    assert isinstance(split, dict)
    assert split.get("source") == "default"
    assert split.get("normalization_applied") is False
    invalid_mix = split.get("invalid_mix")
    assert isinstance(invalid_mix, dict)
    assert invalid_mix.get("reason") == "unsupported_component"

    value = split.get("value")
    assert isinstance(value, dict)
    assert value.get("office") == pytest.approx(50.0)
    assert value.get("residential") == pytest.approx(50.0)


def test_split_contract_changes_recompute_and_scenario_provenance():
    baseline = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="office_residential",
        square_footage=140_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    office_heavy = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="office_residential",
        square_footage=140_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {"components": {"office": 100.0}},
            "description": "mixed-use office residential with 100% office",
        },
    )

    baseline_revenue = baseline.get("revenue_analysis", {}).get("annual_revenue")
    heavy_revenue = office_heavy.get("revenue_analysis", {}).get("annual_revenue")
    assert isinstance(baseline_revenue, (int, float))
    assert isinstance(heavy_revenue, (int, float))
    assert heavy_revenue != pytest.approx(baseline_revenue)

    baseline_dscr = baseline.get("ownership_analysis", {}).get("debt_metrics", {}).get("calculated_dscr")
    heavy_dscr = office_heavy.get("ownership_analysis", {}).get("debt_metrics", {}).get("calculated_dscr")
    assert isinstance(baseline_dscr, (int, float))
    assert isinstance(heavy_dscr, (int, float))
    assert heavy_dscr != pytest.approx(baseline_dscr)

    scenarios = office_heavy.get("dealshield_scenarios")
    assert isinstance(scenarios, dict)
    scenario_inputs = scenarios.get("provenance", {}).get("scenario_inputs")
    assert isinstance(scenario_inputs, dict) and scenario_inputs
    for scenario in scenario_inputs.values():
        assert scenario.get("mixed_use_split_source") == "user_input"
        split = scenario.get("mixed_use_split")
        assert isinstance(split, dict)
        assert split.get("value", {}).get("office") == pytest.approx(100.0)
