import pytest

from app.services.nlp_service import NLPService
from app.v2.config.master_config import BuildingType, ProjectClass
from app.v2.engines.unified_engine import unified_engine


@pytest.fixture
def nlp_service():
    return NLPService()


def _special_feature_breakdown_by_id(result):
    return {
        row["id"]: row
        for row in result["construction_costs"]["special_features_breakdown"]
        if isinstance(row, dict) and row.get("id")
    }


def _calculate_from_description(description: str, *, special_features: list[str]):
    parsed = NLPService().extract_project_details(description)
    result = unified_engine.calculate_project(
        building_type=BuildingType(parsed["building_type"]),
        subtype=parsed["subtype"],
        square_footage=parsed["square_footage"],
        location=parsed["location"],
        project_class=ProjectClass.GROUND_UP,
        special_features=special_features,
        parsed_input_overrides=parsed,
    )
    return parsed, result


@pytest.mark.parametrize(
    ("description", "expected_overrides"),
    (
        (
            "New 24,000 SF ambulatory surgery center with 6 operating rooms in Nashville, TN",
            {"operating_room_count": 6},
        ),
        (
            "New 24,000 SF ambulatory surgery center with 8 ORs in Nashville, TN",
            {"operating_room_count": 8},
        ),
        (
            "New 4,500 SF dental office with 9 operatories in Nashville, TN",
            {"operatory_count": 9},
        ),
        (
            "New 12,000 SF imaging center with 2 MRI suites and 1 CT suite in Nashville, TN",
            {"mri_suite_count": 2, "ct_suite_count": 1},
        ),
        (
            "New 12,000 SF imaging center with 1 PET scan in Nashville, TN",
            {"pet_scan_count": 1},
        ),
        (
            "New 220,000 SF distribution center with 10 loading docks in Nashville, TN",
            {"loading_dock_count": 10, "dock_door_count": 10, "dock_count": 10},
        ),
        (
            "New 220,000 SF distribution center with 8 dock doors in Nashville, TN",
            {"loading_dock_count": 8, "dock_door_count": 8, "dock_count": 8},
        ),
        (
            "New 40,000 SF car dealership with 7 service bays in Nashville, TN",
            {"service_bay_count": 7},
        ),
        (
            "New 120,000 SF manufacturing facility with 3 crane bays in Nashville, TN",
            {"crane_bay_count": 3},
        ),
        (
            "New 6,500 SF quick service restaurant with 2 drive thru lanes in Nashville, TN",
            {"drive_thru_lane_count": 2},
        ),
    ),
)
def test_nlp_extracts_first_wave_special_feature_count_overrides(
    nlp_service,
    description,
    expected_overrides,
):
    parsed = nlp_service.extract_project_details(description)

    for key, expected_value in expected_overrides.items():
        assert parsed.get(key) == expected_value


def test_explicit_operating_room_count_from_prompt_changes_requested_and_billed_quantities():
    description_with_six = (
        "New 24,000 SF ambulatory surgery center with 6 operating rooms in Nashville, TN"
    )
    description_with_eight = (
        "New 24,000 SF ambulatory surgery center with 8 operating rooms in Nashville, TN"
    )

    parsed_six, result_six = _calculate_from_description(
        description_with_six,
        special_features=["operating_room"],
    )
    parsed_eight, result_eight = _calculate_from_description(
        description_with_eight,
        special_features=["operating_room"],
    )

    six_row = _special_feature_breakdown_by_id(result_six)["operating_room"]
    eight_row = _special_feature_breakdown_by_id(result_eight)["operating_room"]

    assert parsed_six["operating_room_count"] == 6
    assert parsed_eight["operating_room_count"] == 8
    assert six_row["requested_quantity"] == pytest.approx(6.0)
    assert six_row["billed_quantity"] == pytest.approx(0.0)
    assert six_row["total_cost"] == pytest.approx(0.0)
    assert eight_row["requested_quantity"] == pytest.approx(8.0)
    assert eight_row["billed_quantity"] == pytest.approx(2.0)
    assert eight_row["requested_quantity_source"] == "explicit_override:operating_room_count"
    assert eight_row["total_cost"] == pytest.approx(900000.0)
    assert (
        result_six["construction_costs"]["special_features_total"]
        < result_eight["construction_costs"]["special_features_total"]
    )


def test_explicit_loading_dock_count_from_prompt_reaches_overage_pricing():
    parsed, result = _calculate_from_description(
        "New 220,000 SF distribution center with 10 loading docks in Nashville, TN",
        special_features=["extra_loading_docks"],
    )

    row = _special_feature_breakdown_by_id(result)["extra_loading_docks"]

    assert parsed["loading_dock_count"] == 10
    assert parsed["dock_door_count"] == 10
    assert parsed["dock_count"] == 10
    assert row["requested_quantity"] == pytest.approx(10.0)
    assert row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row["included_baseline_quantity"] == pytest.approx(8.0)
    assert row["billed_quantity"] == pytest.approx(2.0)
    assert row["total_cost"] == pytest.approx(130000.0)


def test_explicit_service_bay_count_from_prompt_reaches_overage_pricing():
    parsed, result = _calculate_from_description(
        "New 40,000 SF car dealership with 10 service bays in Nashville, TN",
        special_features=["expanded_service_bays"],
    )

    row = _special_feature_breakdown_by_id(result)["expanded_service_bays"]

    assert parsed["service_bay_count"] == 10
    assert row["requested_quantity"] == pytest.approx(10.0)
    assert row["requested_quantity_source"] == "explicit_override:service_bay_count"
    assert row["included_baseline_quantity"] == pytest.approx(8.0)
    assert row["billed_quantity"] == pytest.approx(2.0)
    assert row["total_cost"] == pytest.approx(190000.0)


def test_explicit_crane_bay_count_from_prompt_reaches_count_based_pricing():
    parsed, result = _calculate_from_description(
        "New 120,000 SF manufacturing facility with 3 crane bays in Nashville, TN",
        special_features=["crane_bays"],
    )

    row = _special_feature_breakdown_by_id(result)["crane_bays"]

    assert parsed["crane_bay_count"] == 3
    assert row["requested_quantity"] == pytest.approx(3.0)
    assert row["requested_quantity_source"] == "explicit_override:crane_bay_count"
    assert row["included_baseline_quantity"] == pytest.approx(2.0)
    assert row["billed_quantity"] == pytest.approx(1.0)
    assert row["total_cost"] == pytest.approx(300000.0)


def test_no_explicit_count_prompt_preserves_current_default_behavior():
    parsed, result = _calculate_from_description(
        "New 24,000 SF ambulatory surgery center in Nashville, TN",
        special_features=["operating_room"],
    )

    row = _special_feature_breakdown_by_id(result)["operating_room"]

    assert "operating_room_count" not in parsed
    assert row["requested_quantity"] == pytest.approx(6.0)
    assert row["requested_quantity_source"] == "size_band_default"
    assert row["included_baseline_quantity"] == pytest.approx(6.0)
    assert row["billed_quantity"] == pytest.approx(6.0)
    assert row["total_cost"] == pytest.approx(0.0)
