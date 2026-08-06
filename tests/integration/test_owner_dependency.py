"""Integration test for configuration-owned current-user resolution."""

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID, uuid4

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from apps.api.dependencies import get_current_owner, get_database_session
from apps.api.schemas import UserRead
from bridge_surface.config import Settings, get_settings
from bridge_surface.models import User
from bridge_surface.persistence import create_session_factory, session_scope


@pytest.mark.anyio
async def test_dependency_resolves_configured_owner_without_request_selected_id(
    migrated_database_engine: Engine,
) -> None:
    configured_id = UUID("22222222-2222-4222-8222-222222222222")
    settings = Settings(  # type: ignore[call-arg]
        _env_file=None,
        local_user_id=configured_id,
        local_user_display_name="Dependency Owner",
        local_user_preferred_language="ja",
    )
    factory = create_session_factory(migrated_database_engine)

    def override_session() -> Iterator[Session]:
        with session_scope(factory) as session:
            yield session

    def override_settings() -> Settings:
        return settings

    def read_owner(owner: Annotated[User, Depends(get_current_owner)]) -> User:
        return owner

    test_app = FastAPI()
    test_app.add_api_route("/owner", read_owner, response_model=UserRead)
    test_app.dependency_overrides[get_database_session] = override_session
    test_app.dependency_overrides[get_settings] = override_settings

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/owner",
            params={"owner_id": str(uuid4()), "user_id": str(uuid4())},
        )

    assert response.status_code == 200
    assert response.json()["id"] == str(configured_id)
    assert response.json()["display_name"] == "Dependency Owner"
    assert response.json()["preferred_language"] == "ja"

    with session_scope(factory) as session:
        persisted_ids = list(session.scalars(select(User.id)))

    assert persisted_ids == [configured_id]
