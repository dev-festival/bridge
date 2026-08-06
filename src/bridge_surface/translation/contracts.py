"""Provider-neutral translation request and result contracts."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContractModel(BaseModel):
    """Immutable base for data exchanged across the provider boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Language(StrEnum):
    """Languages supported by the first Bridge Surface release."""

    JAPANESE = "ja"
    ENGLISH = "en"


class WarningSeverity(StrEnum):
    """Provider-neutral warning severity values."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PreservationReason(StrEnum):
    """Why a source fragment was retained in translated output."""

    IDENTIFIER = "identifier"
    NUMERIC_VALUE = "numeric_value"
    CONTEXT_TERM = "context_term"


class ProviderMode(StrEnum):
    """Whether a result came from deterministic local behavior or an external service."""

    MOCK = "mock"
    EXTERNAL = "external"


class PreservedTerm(ContractModel):
    """A source fragment that the provider kept unchanged."""

    term: str = Field(min_length=1, max_length=200)
    reason: PreservationReason


class TranslationWarning(ContractModel):
    """Structured advisory feedback returned with a translation."""

    code: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9_]+$")
    message: str = Field(min_length=1, max_length=500)
    severity: WarningSeverity


class ProviderMetadata(ContractModel):
    """Allowlisted, non-secret metadata safe for persistence and display."""

    provider_name: str = Field(min_length=1, max_length=80)
    provider_mode: ProviderMode
    model_name: str | None = Field(default=None, max_length=120)
    fixture_id: str | None = Field(default=None, max_length=120)


class TranslationContext(ContractModel):
    """Optional business context and exact fragments the provider must preserve."""

    business_context: str | None = Field(default=None, max_length=2_000)
    preserve_terms: tuple[str, ...] = ()

    @field_validator("preserve_terms")
    @classmethod
    def validate_preserve_terms(cls, terms: tuple[str, ...]) -> tuple[str, ...]:
        """Reject blank or duplicate preservation instructions."""

        if any(not term.strip() for term in terms):
            raise ValueError("Preserved terms must not be blank.")
        if len(set(terms)) != len(terms):
            raise ValueError("Preserved terms must be unique.")
        return terms


class TranslationResult(ContractModel):
    """Complete provider-neutral result for one translation request."""

    translated_text: str = Field(min_length=1)
    detected_source_language: Language
    reverse_translation: str = Field(min_length=1)
    preserved_terms: tuple[PreservedTerm, ...] = ()
    ambiguous_terms: tuple[str, ...] = ()
    warnings: tuple[TranslationWarning, ...] = ()
    confidence: float | None = Field(default=None, ge=0, le=1)
    provider_metadata: ProviderMetadata
