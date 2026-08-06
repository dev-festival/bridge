"""Schemas for operational API responses."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Non-sensitive process health response."""

    status: str
    service: str
    api_version: str
