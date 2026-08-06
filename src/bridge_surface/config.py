"""Application settings and the allowlisted public configuration view."""

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bridge_surface import __version__


class PublicConfig(BaseModel):
    """Configuration values that are safe to return to an unauthenticated client."""

    app_name: str
    environment: str
    api_version: str
    debug: bool


class Settings(BaseSettings):
    """Process settings loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BRIDGE_",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Bridge Surface"
    environment: Literal["development", "test", "production"] = "development"
    api_prefix: str = Field(default="/api/v1", pattern=r"^/[a-zA-Z0-9/_-]+$")
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    def public_config(self) -> PublicConfig:
        """Return an explicit allowlist rather than serializing all process settings."""

        return PublicConfig(
            app_name=self.app_name,
            environment=self.environment,
            api_version=__version__,
            debug=self.debug,
        )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable-by-convention settings instance."""

    return Settings()
