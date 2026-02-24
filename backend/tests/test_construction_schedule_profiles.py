import pytest

from app.v2.config.master_config import BuildingType
from app.v2.engines.unified_engine import build_construction_schedule


TARGET_SUBTYPE_EXPECTATIONS = [
    (BuildingType.OFFICE, "class_a", 30),
    (BuildingType.OFFICE, "class_b", 24),
    (BuildingType.INDUSTRIAL, "warehouse", 16),
    (BuildingType.INDUSTRIAL, "distribution_center", 20),
    (BuildingType.INDUSTRIAL, "manufacturing", 24),
    (BuildingType.INDUSTRIAL, "flex_space", 19),
    (BuildingType.INDUSTRIAL, "cold_storage", 22),
    (BuildingType.MULTIFAMILY, "market_rate_apartments", 28),
    (BuildingType.MULTIFAMILY, "luxury_apartments", 34),
    (BuildingType.MULTIFAMILY, "affordable_housing", 26),
    (BuildingType.RESTAURANT, "quick_service", 12),
    (BuildingType.RESTAURANT, "full_service", 15),
    (BuildingType.RESTAURANT, "fine_dining", 17),
    (BuildingType.RESTAURANT, "cafe", 11),
    (BuildingType.RESTAURANT, "bar_tavern", 16),
    (BuildingType.RETAIL, "shopping_center", 20),
    (BuildingType.RETAIL, "big_box", 18),
    (BuildingType.HOSPITALITY, "limited_service_hotel", 24),
    (BuildingType.HOSPITALITY, "full_service_hotel", 32),
    (BuildingType.SPECIALTY, "data_center", 26),
    (BuildingType.SPECIALTY, "laboratory", 22),
    (BuildingType.SPECIALTY, "self_storage", 15),
    (BuildingType.SPECIALTY, "car_dealership", 18),
    (BuildingType.SPECIALTY, "broadcast_facility", 20),
    (BuildingType.HEALTHCARE, "surgical_center", 15),
    (BuildingType.HEALTHCARE, "imaging_center", 17),
    (BuildingType.HEALTHCARE, "urgent_care", 13),
    (BuildingType.HEALTHCARE, "outpatient_clinic", 14),
    (BuildingType.HEALTHCARE, "medical_office_building", 18),
    (BuildingType.HEALTHCARE, "dental_office", 12),
    (BuildingType.HEALTHCARE, "hospital", 30),
    (BuildingType.HEALTHCARE, "medical_center", 24),
    (BuildingType.HEALTHCARE, "nursing_home", 20),
    (BuildingType.HEALTHCARE, "rehabilitation", 16),
]


@pytest.mark.parametrize(
    "building_type,subtype,expected_total_months",
    TARGET_SUBTYPE_EXPECTATIONS,
)
def test_subtype_schedules_resolve_for_target_verticals(
    building_type,
    subtype,
    expected_total_months,
):
    schedule = build_construction_schedule(building_type, subtype=subtype)

    assert schedule["building_type"] == building_type.value
    assert schedule["subtype"] == subtype
    assert schedule["schedule_source"] == "subtype"
    assert schedule["total_months"] == expected_total_months
    assert isinstance(schedule["phases"], list) and schedule["phases"]

    for phase in schedule["phases"]:
        assert isinstance(phase.get("id"), str) and phase["id"]
        assert isinstance(phase.get("label"), str) and phase["label"]
        assert isinstance(phase.get("start_month"), int)
        assert isinstance(phase.get("duration_months"), int)
        assert isinstance(phase.get("end_month"), int)
        assert phase["start_month"] <= phase["end_month"] <= schedule["total_months"]


@pytest.mark.parametrize(
    "building_type,unknown_subtype,expected_total_months",
    [
        (BuildingType.OFFICE, "class_c_reposition", 27),
        (BuildingType.INDUSTRIAL, "unknown_dc_variant", 18),
        (BuildingType.MULTIFAMILY, "student_housing_variant", 30),
        (BuildingType.RESTAURANT, "chef_counter_concept", 14),
        (BuildingType.RETAIL, "unknown_retail_variant", 27),
        (BuildingType.HOSPITALITY, "unknown_hotel_variant", 30),
        (BuildingType.SPECIALTY, "unknown_specialty_variant", 27),
        (BuildingType.HEALTHCARE, "unknown_healthcare_variant", 16),
    ],
)
def test_unknown_subtype_falls_back_to_building_type_schedule(
    building_type,
    unknown_subtype,
    expected_total_months,
):
    schedule = build_construction_schedule(building_type, subtype=unknown_subtype)

    assert schedule["building_type"] == building_type.value
    assert schedule["subtype"] is None
    assert schedule["schedule_source"] == "building_type"
    assert schedule["total_months"] == expected_total_months


def test_unknown_hospitality_subtype_falls_back_to_multifamily_baseline_deterministically():
    hospitality_fallback = build_construction_schedule(
        BuildingType.HOSPITALITY,
        subtype="hotel_variant_not_configured",
    )
    multifamily_baseline = build_construction_schedule(BuildingType.MULTIFAMILY)

    assert hospitality_fallback["building_type"] == BuildingType.HOSPITALITY.value
    assert hospitality_fallback["subtype"] is None
    assert hospitality_fallback["schedule_source"] == "building_type"
    assert hospitality_fallback["total_months"] == multifamily_baseline["total_months"]
    assert hospitality_fallback["phases"] == multifamily_baseline["phases"]


def test_non_target_building_types_keep_existing_behavior():
    parking_schedule = build_construction_schedule(BuildingType.PARKING, subtype="garage")
    industrial_default_schedule = build_construction_schedule(BuildingType.INDUSTRIAL)

    assert parking_schedule["building_type"] == BuildingType.PARKING.value
    assert parking_schedule["subtype"] is None
    assert parking_schedule["schedule_source"] == "building_type"
    assert parking_schedule["total_months"] == industrial_default_schedule["total_months"]
    assert parking_schedule["phases"] == industrial_default_schedule["phases"]
