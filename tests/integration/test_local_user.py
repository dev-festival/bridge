"""Integration tests for the local user repository and bootstrap service."""

from typing import Literal
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from bridge_surface.config import Settings
from bridge_surface.models import User
from bridge_surface.repositories import UserRepository
from bridge_surface.services import LocalUserConflictError, bootstrap_local_user

DEFAULT_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


def local_settings(
    *,
    user_id: UUID = DEFAULT_USER_ID,
    display_name: str = "Local User",
    preferred_language: Literal["ja", "en"] = "en",
) -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        local_user_id=user_id,
        local_user_display_name=display_name,
        local_user_preferred_language=preferred_language,
    )


def test_bootstrap_creates_the_configured_user(database_session: Session) -> None:
    settings = local_settings(preferred_language="ja")

    user = bootstrap_local_user(database_session, settings)
    repository = UserRepository(database_session)

    assert user.id == settings.local_user_id
    assert user.display_name == "Local User"
    assert user.preferred_language == "ja"
    assert user.created_at is not None
    assert user.updated_at is not None
    assert repository.count() == 1
    assert repository.get_by_id(settings.local_user_id) is user


def test_bootstrap_is_idempotent_and_synchronizes_configured_profile(
    database_session: Session,
) -> None:
    initial = bootstrap_local_user(database_session, local_settings())

    repeated = bootstrap_local_user(
        database_session,
        local_settings(display_name="Updated Owner", preferred_language="ja"),
    )

    assert repeated.id == initial.id
    assert repeated.display_name == "Updated Owner"
    assert repeated.preferred_language == "ja"
    assert UserRepository(database_session).count() == 1


def test_bootstrap_refuses_to_create_a_second_local_owner(database_session: Session) -> None:
    repository = UserRepository(database_session)
    repository.add(
        User(
            id=uuid4(),
            display_name="Unexpected User",
            preferred_language="en",
        )
    )
    database_session.commit()

    with pytest.raises(LocalUserConflictError, match="second local owner"):
        bootstrap_local_user(database_session, local_settings())

    assert repository.count() == 1


def test_bootstrap_rejects_an_existing_multi_user_state(database_session: Session) -> None:
    bootstrap_local_user(database_session, local_settings())
    repository = UserRepository(database_session)
    repository.add(
        User(
            id=uuid4(),
            display_name="Unexpected User",
            preferred_language="en",
        )
    )
    database_session.commit()

    with pytest.raises(LocalUserConflictError, match="Multiple users exist"):
        bootstrap_local_user(database_session, local_settings())
