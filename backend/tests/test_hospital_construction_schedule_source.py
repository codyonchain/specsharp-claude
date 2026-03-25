import asyncio
from typing import Dict, Tuple

from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.v2.api.scope import AnalyzeRequest, analyze_project
from app.v2.config.construction_schedule import build_construction_schedule
from app.v2.config.master_config import BuildingType, OwnershipType, ProjectClass
from app.v2.engines.unified_engine import build_project_timeline, unified_engine


ANCHOR_DESCRIPTION = (
    "New 240,000 SF hospital with 12 OR surgical suite, emergency department, "
    "imaging suite, laboratory, ICU, and cath lab in Nashville, TN"
)


def _build_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v2/analyze",
            "headers": [],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("localhost", 8000),
            "scheme": "http",
            "root_path": "",
            "http_version": "1.1",
        }
    )


def _analyze_hospital() -> Tuple[Dict[str, object], Dict[str, object]]:
    payload = AnalyzeRequest(
        description=ANCHOR_DESCRIPTION,
        squareFootage=240_000,
        location="Nashville, TN",
        projectClass="ground_up",
    )

    response = asyncio.run(
        analyze_project(
            _build_request(),
            payload,
            build_testing_auth_context(),
        )
    )

    assert response.success is True, response.errors
    return response.data["parsed_input"], response.data["calculations"]


def test_unified_engine_emits_hospital_schedule_contract_for_active_path():
    calculations = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="hospital",
        square_footage=240_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        floors=4,
        ownership_type=OwnershipType.FOR_PROFIT,
        finish_level="standard",
        finish_level_source="explicit",
        special_features=[],
        parsed_input_overrides={"operating_room_count": 12},
    )

    expected_schedule = build_construction_schedule(BuildingType.HEALTHCARE, subtype="hospital")
    expected_timeline = build_project_timeline(BuildingType.HEALTHCARE, None)

    assert calculations["construction_schedule"] == expected_schedule
    assert calculations["project_timeline"] == expected_timeline


def test_analyze_project_returns_hospital_schedule_from_backend_contract():
    parsed, calculations = _analyze_hospital()
    expected_schedule = build_construction_schedule(BuildingType.HEALTHCARE, subtype="hospital")
    expected_timeline = build_project_timeline(BuildingType.HEALTHCARE, None)

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "hospital"
    assert calculations["construction_schedule"] == expected_schedule
    assert calculations["project_timeline"] == expected_timeline
    assert calculations["construction_schedule"]["schedule_source"] == "subtype"
    assert calculations["construction_schedule"]["total_months"] == 30
    assert [phase["label"] for phase in calculations["construction_schedule"]["phases"]] == [
        "Planning, Licensing + Program Approvals",
        "Tower/Shell + Critical MEP Rough-In",
        "Inpatient + Procedural Interior Buildout",
        "Clinical Equipment + Integrated Low Voltage",
        "Integrated Systems Commissioning",
        "Operational Readiness + Service Activation",
    ]
