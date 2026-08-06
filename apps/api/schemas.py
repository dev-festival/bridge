"""Schemas for operational API responses."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Non-sensitive process health response."""

    status: str
    service: str
    api_version: str


class UserRead(BaseModel):
    """Read-only representation of the configured local owner."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    preferred_language: Literal["ja", "en"]
    created_at: datetime
    updated_at: datetime
