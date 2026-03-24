import asyncio

import pytest
from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.core.building_taxonomy import validate_building_type
from app.v2.api.scope import AnalyzeRequest, analyze_project


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


def test_medical_office_alias_normalizes_to_medical_office_building():
    building_type, subtype = validate_building_type("healthcare", "medical_office")

    assert building_type == "healthcare"
    assert subtype == "medical_office_building"


def test_medical_office_building_remains_canonical():
    building_type, subtype = validate_building_type("healthcare", "medical_office_building")

    assert building_type == "healthcare"
    assert subtype == "medical_office_building"


def test_mixed_use_normalization_is_unchanged():
    building_type, subtype = validate_building_type("mixed_use", "retail_residential")

    assert building_type == "mixed_use"
    assert subtype == "retail_residential"


def test_analyze_project_accepts_medical_office_building_alias_path():
    payload = AnalyzeRequest(
        description="New 120,000 SF medical office building with tenant improvements in Nashville, TN",
        squareFootage=120_000,
        location="Nashville, TN",
        projectClass="ground_up",
        special_features=["tenant_improvements"],
    )

    response = asyncio.run(
        analyze_project(
            _build_request(),
            payload,
            build_testing_auth_context(),
        )
    )

    assert response.success is True
    assert response.errors is None
    assert response.data["parsed_input"]["building_type"] == "healthcare"
    assert response.data["parsed_input"]["subtype"] == "medical_office_building"
    assert response.data["calculations"]["project_info"]["subtype"] == "medical_office_building"
    assert response.data["calculations"]["construction_costs"]["special_features_total"] == pytest.approx(
        3_600_000.0
    )
