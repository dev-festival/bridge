"""Translation provider protocol and boundary errors."""

from typing import Protocol, runtime_checkable

from bridge_surface.translation.contracts import Language, TranslationContext, TranslationResult


class TranslationProviderError(ValueError):
    """Base error raised for invalid provider-boundary requests."""


class EmptySourceTextError(TranslationProviderError):
    """Raised when a translation request contains no source text."""


class UnsupportedLanguageError(TranslationProviderError):
    """Raised when a request uses a language outside Japanese and English."""


class InvalidLanguagePairError(TranslationProviderError):
    """Raised when source and target languages are identical."""


@runtime_checkable
class TranslationProvider(Protocol):
    """Provider-neutral async translation interface."""

    provider_name: str

    async def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
        context: TranslationContext,
    ) -> TranslationResult:
        """Translate source text and return validation artifacts."""
