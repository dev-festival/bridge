"""Establish the empty migration baseline.

Revision ID: 0001_empty_baseline
Revises:
Create Date: 2026-08-06
"""

from collections.abc import Sequence

revision: str = "0001_empty_baseline"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish the initial empty migration baseline."""


def downgrade() -> None:
    """Return to the state before migration tracking."""
