"""FastAPI dependencies shared by future product routes."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from bridge_surface.config import Settings, get_settings
from bridge_surface.models import User
from bridge_surface.persistence import (
    create_database_engine,
    create_session_factory,
    session_scope,
)
from bridge_surface.services import LocalUserConflictError, bootstrap_local_user

_engine = create_database_engine(get_settings().database_url)
_session_factory = create_session_factory(_engine)


def get_database_session() -> Iterator[Session]:
    """Provide one session without creating or migrating schema."""

    with session_scope(_session_factory) as session:
        yield session


def get_current_owner(
    session: Annotated[Session, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Resolve the configuration-selected local owner without request input."""

    try:
        return bootstrap_local_user(session, settings)
    except LocalUserConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local owner configuration conflicts with persisted user data.",
        ) from error
