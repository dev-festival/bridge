"""FastAPI entry point for Bridge Surface."""

from fastapi import FastAPI

from apps.api.schemas import HealthResponse
from bridge_surface import __version__
from bridge_surface.config import PublicConfig, get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    debug=settings.debug,
)


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health() -> HealthResponse:
    """Report that the API process is available without probing future dependencies."""

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        api_version=__version__,
    )


@app.get(f"{settings.api_prefix}/config", response_model=PublicConfig, tags=["operations"])
def public_config() -> PublicConfig:
    """Return only configuration values intentionally safe for public clients."""

    return settings.public_config()
