"""Persistence operations for the configured local user."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bridge_surface.models import User


class UserRepository:
    """Provide only the user persistence operations required by local bootstrap."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by primary key."""

        return self._session.get(User, user_id)

    def count(self) -> int:
        """Count all persisted users to enforce the local single-user invariant."""

        count = self._session.scalar(select(func.count()).select_from(User))
        return int(count or 0)

    def add(self, user: User) -> None:
        """Stage a new local user in the current transaction."""

        self._session.add(user)

    def update_profile(self, user: User, *, display_name: str, preferred_language: str) -> bool:
        """Synchronize configuration-owned profile fields and report whether they changed."""

        changed = user.display_name != display_name or user.preferred_language != preferred_language
        if changed:
            user.display_name = display_name
            user.preferred_language = preferred_language
        return changed
