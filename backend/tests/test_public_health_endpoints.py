import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_health_exposes_only_public_liveness_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "SpecSharp API",
    }


@pytest.mark.asyncio
async def test_v2_health_exposes_only_minimal_public_status():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        response = await client.get("/api/v2/health")

    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"] == {"status": "healthy"}
    assert "version" not in payload["data"]
    assert "engine" not in payload["data"]
    assert "building_types" not in payload["data"]
    assert "total_subtypes" not in payload["data"]
    assert "features" not in payload["data"]
