"""Provider-neutral translation boundary and local mock implementation."""

from bridge_surface.translation.contracts import (
    Language,
    PreservationReason,
    PreservedTerm,
    ProviderMetadata,
    ProviderMode,
    TranslationContext,
    TranslationResult,
    TranslationWarning,
    WarningSeverity,
)
from bridge_surface.translation.factory import UnsupportedProviderError, create_translation_provider
from bridge_surface.translation.mock import MockTranslationProvider
from bridge_surface.translation.provider import (
    EmptySourceTextError,
    InvalidLanguagePairError,
    TranslationProvider,
    TranslationProviderError,
    UnsupportedLanguageError,
)

__all__ = [
    "EmptySourceTextError",
    "InvalidLanguagePairError",
    "Language",
    "MockTranslationProvider",
    "PreservationReason",
    "PreservedTerm",
    "ProviderMetadata",
    "ProviderMode",
    "TranslationContext",
    "TranslationProvider",
    "TranslationProviderError",
    "TranslationResult",
    "TranslationWarning",
    "UnsupportedLanguageError",
    "UnsupportedProviderError",
    "WarningSeverity",
    "create_translation_provider",
]
