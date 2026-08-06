"""Translation provider construction."""

from bridge_surface.translation.mock import MockTranslationProvider
from bridge_surface.translation.provider import TranslationProvider, TranslationProviderError


class UnsupportedProviderError(TranslationProviderError):
    """Raised when configuration names a provider not implemented by this build."""


def create_translation_provider(provider_name: str | None = None) -> TranslationProvider:
    """Create the configured provider, defaulting to credential-free mock behavior."""

    normalized_name = (provider_name or "mock").strip().lower()
    if normalized_name == "mock":
        return MockTranslationProvider()
    raise UnsupportedProviderError(f"Unsupported translation provider: {provider_name!r}.")
