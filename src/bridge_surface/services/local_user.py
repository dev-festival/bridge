"""Idempotent bootstrap service for the configured local owner."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from bridge_surface.config import Settings
from bridge_surface.models import User
from bridge_surface.repositories import UserRepository


class LocalUserConflictError(RuntimeError):
    """Raised when existing user data conflicts with single-local-user mode."""


def bootstrap_local_user(session: Session, settings: Settings) -> User:
    """Create or synchronize exactly one configuration-selected local owner."""

    repository = UserRepository(session)
    existing = repository.get_by_id(settings.local_user_id)
    if existing is not None:
        if repository.count() != 1:
            raise LocalUserConflictError(
                "Multiple users exist; refusing to resolve an ambiguous local owner."
            )
        changed = repository.update_profile(
            existing,
            display_name=settings.local_user_display_name,
            preferred_language=settings.local_user_preferred_language,
        )
        if changed:
            session.commit()
            session.refresh(existing)
        return existing

    if repository.count() != 0:
        raise LocalUserConflictError(
            "A different user already exists; refusing to create a second local owner."
        )

    user = User(
        id=settings.local_user_id,
        display_name=settings.local_user_display_name,
        preferred_language=settings.local_user_preferred_language,
    )
    repository.add(user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        concurrent_user = repository.get_by_id(settings.local_user_id)
        if concurrent_user is None:
            raise
        return concurrent_user

    session.refresh(user)
    return user
