"""Local user persistence model."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from bridge_surface.persistence import Base


def utc_now() -> datetime:
    """Return the current UTC time for ORM-managed timestamp updates."""

    return datetime.now(UTC)


class User(Base):
    """The single configured local owner for the MVP."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "preferred_language IN ('ja', 'en')",
            name="ck_users_preferred_language",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.current_timestamp(),
        nullable=False,
    )
