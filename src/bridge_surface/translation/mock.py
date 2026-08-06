"""Credential-free deterministic translation provider."""

import re

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
from bridge_surface.translation.fixtures import FIXTURES, BilingualFixture
from bridge_surface.translation.provider import (
    EmptySourceTextError,
    InvalidLanguagePairError,
    UnsupportedLanguageError,
)

_TECHNICAL_TERM_PATTERN = re.compile(
    r"(?:Drawing\s+[A-Z0-9]+(?:-[A-Z0-9]+)*|[A-Z]{2,}-?\d[A-Z0-9-]*|"
    r"\d+(?:\.\d+)?\s*(?:mm|AM|PM))(?![A-Za-z0-9_-])"
)


class MockTranslationProvider:
    """Translate known fixtures and return labeled placeholders for all other text."""

    provider_name = "mock"

    async def translate(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
        context: TranslationContext,
    ) -> TranslationResult:
        """Return a deterministic result without credentials, I/O, or network access."""

        self._validate_request(text, source_language, target_language)
        fixture = self._find_fixture(text, source_language)
        if fixture is not None:
            return self._fixture_result(fixture, text, source_language, context)
        return self._fallback_result(text, source_language, target_language, context)

    @staticmethod
    def _validate_request(
        text: str,
        source_language: Language,
        target_language: Language,
    ) -> None:
        if not text.strip():
            raise EmptySourceTextError("Source text must not be blank.")
        if not isinstance(source_language, Language):
            raise UnsupportedLanguageError(f"Unsupported source language: {source_language!r}.")
        if not isinstance(target_language, Language):
            raise UnsupportedLanguageError(f"Unsupported target language: {target_language!r}.")
        if source_language == target_language:
            raise InvalidLanguagePairError("Source and target languages must be different.")

    @staticmethod
    def _find_fixture(text: str, source_language: Language) -> BilingualFixture | None:
        for fixture in FIXTURES:
            source_text = (
                fixture.english_text
                if source_language is Language.ENGLISH
                else fixture.japanese_text
            )
            if text == source_text:
                return fixture
        return None

    def _fixture_result(
        self,
        fixture: BilingualFixture,
        source_text: str,
        source_language: Language,
        context: TranslationContext,
    ) -> TranslationResult:
        translated_text = (
            fixture.japanese_text if source_language is Language.ENGLISH else fixture.english_text
        )
        return TranslationResult(
            translated_text=translated_text,
            detected_source_language=source_language,
            reverse_translation=source_text,
            preserved_terms=self._collect_preserved_terms(
                source_text,
                fixture.preserved_terms,
                context,
            ),
            provider_metadata=self._metadata(fixture.fixture_id),
        )

    def _fallback_result(
        self,
        text: str,
        source_language: Language,
        target_language: Language,
        context: TranslationContext,
    ) -> TranslationResult:
        translated_text = self._fallback_translation(text, source_language, target_language)
        reverse_translation = self._fallback_reverse(text, source_language)
        return TranslationResult(
            translated_text=translated_text,
            detected_source_language=source_language,
            reverse_translation=reverse_translation,
            preserved_terms=self._collect_preserved_terms(text, (), context),
            warnings=(
                TranslationWarning(
                    code="mock_fallback",
                    message=(
                        "No explicit bilingual fixture matched; returned a labeled "
                        "deterministic placeholder."
                    ),
                    severity=WarningSeverity.INFO,
                ),
            ),
            provider_metadata=self._metadata(None),
        )

    @staticmethod
    def _fallback_translation(
        text: str,
        source_language: Language,
        target_language: Language,
    ) -> str:
        if source_language is Language.ENGLISH and target_language is Language.JAPANESE:
            return f"【モック翻訳(英語→日本語)】{text}"
        return f"[MOCK translation (Japanese→English)] {text}"

    @staticmethod
    def _fallback_reverse(text: str, source_language: Language) -> str:
        if source_language is Language.ENGLISH:
            return f"[MOCK reverse translation to English] {text}"
        return f"【モック逆翻訳(日本語)】{text}"

    @staticmethod
    def _collect_preserved_terms(
        text: str,
        fixture_terms: tuple[PreservedTerm, ...],
        context: TranslationContext,
    ) -> tuple[PreservedTerm, ...]:
        terms_by_text = {item.term: item for item in fixture_terms}

        for match in _TECHNICAL_TERM_PATTERN.finditer(text):
            term = match.group(0)
            reason = (
                PreservationReason.NUMERIC_VALUE
                if term[0].isdigit()
                else PreservationReason.IDENTIFIER
            )
            terms_by_text.setdefault(term, PreservedTerm(term=term, reason=reason))

        for term in context.preserve_terms:
            if term in text:
                terms_by_text.setdefault(
                    term,
                    PreservedTerm(term=term, reason=PreservationReason.CONTEXT_TERM),
                )

        return tuple(
            sorted(
                terms_by_text.values(),
                key=lambda item: (text.index(item.term), item.term),
            )
        )

    @staticmethod
    def _metadata(fixture_id: str | None) -> ProviderMetadata:
        return ProviderMetadata(
            provider_name="mock",
            provider_mode=ProviderMode.MOCK,
            model_name="deterministic-fixtures-v1",
            fixture_id=fixture_id,
        )
