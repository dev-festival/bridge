"""Integration tests for the operational FastAPI endpoints."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.anyio
async def test_health_endpoint_is_non_secret_and_healthy(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Bridge Surface",
        "api_version": "0.1.0",
    }


@pytest.mark.anyio
async def test_public_config_endpoint_returns_only_allowlisted_fields(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/config")

    assert response.status_code == 200
    assert response.json() == {
        "app_name": "Bridge Surface",
        "environment": "development",
        "api_version": "0.1.0",
        "debug": False,
    }


@pytest.mark.anyio
async def test_unknown_route_returns_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/not-a-real-route")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
