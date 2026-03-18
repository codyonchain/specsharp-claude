import logging

import pytest
from starlette.requests import Request

from app.core.auth import AuthContext
from app.v2.api import scope as scope_api


class _RollbackOnlyDB:
    def __init__(self) -> None:
        self.rollback_called = False

    def rollback(self) -> None:
        self.rollback_called = True


def _auth() -> AuthContext:
    return AuthContext(
        user_id="user_1",
        email="user@example.com",
        org_id="org_1",
        role="owner",
        access_token="token",
    )


def _request(request_id: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v2/scope/analyze",
            "headers": [(b"x-request-id", request_id.encode("utf-8"))],
        }
    )


@pytest.mark.asyncio
async def test_analyze_project_does_not_log_raw_description_and_returns_bounded_error(
    monkeypatch,
    caplog,
):
    raw_description = "Confidential 180,000 sf mixed-use tower at 123 Main Street in Dallas, TX"
    internal_error = "parser exploded while reading Confidential 180,000 sf mixed-use tower"
    request = _request("req-analyze-1")
    payload = scope_api.AnalyzeRequest(description=raw_description)

    def _raise_parser_failure(_description: str):
        raise RuntimeError(internal_error)

    monkeypatch.setattr(scope_api.nlp_service, "extract_project_details", _raise_parser_failure)
    caplog.set_level(logging.INFO, logger=scope_api.logger.name)

    response = await scope_api.analyze_project(request, payload, _auth())

    assert response.success is False
    assert response.errors == [scope_api.ANALYZE_ERROR_MESSAGE]
    assert raw_description not in caplog.text
    assert internal_error not in caplog.text
    assert "request_id=req-analyze-1" in caplog.text
    assert "exception_type=RuntimeError" in caplog.text


@pytest.mark.asyncio
async def test_generate_scope_returns_bounded_error_without_logging_raw_description(
    monkeypatch,
    caplog,
):
    raw_description = "Confidential full-service hotel conversion for stealth hospitality deal"
    internal_error = "engine failed for Confidential full-service hotel conversion"
    request = _request("req-generate-1")
    payload = scope_api.AnalyzeRequest(
        description=raw_description,
        location="Nashville, TN",
        square_footage=85000,
    )
    db = _RollbackOnlyDB()

    monkeypatch.setattr(scope_api, "assert_run_available", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        scope_api.nlp_service,
        "extract_project_details",
        lambda _description: {
            "building_type": "hospitality",
            "subtype": "full_service_hotel",
            "square_footage": 85000,
            "location": "Nashville, TN",
            "project_class": "ground_up",
        },
    )

    def _raise_engine_failure(**_kwargs):
        raise RuntimeError(internal_error)

    monkeypatch.setattr(scope_api.unified_engine, "calculate_project", _raise_engine_failure)
    caplog.set_level(logging.INFO, logger=scope_api.logger.name)

    response = await scope_api.generate_scope(request, payload, db, _auth())

    assert db.rollback_called is True
    assert response.success is False
    assert response.errors == [scope_api.GENERATE_ERROR_MESSAGE]
    assert raw_description not in caplog.text
    assert internal_error not in caplog.text
    assert "request_id=req-generate-1" in caplog.text
    assert "exception_type=RuntimeError" in caplog.text
