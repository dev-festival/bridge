"""Tests for immutable provider-neutral translation contracts."""

import pytest
from pydantic import ValidationError

from bridge_surface.translation import (
    Language,
    MockTranslationProvider,
    ProviderMetadata,
    ProviderMode,
    TranslationContext,
    TranslationProvider,
    TranslationResult,
)


def test_mock_conforms_to_runtime_provider_protocol() -> None:
    provider: TranslationProvider = MockTranslationProvider()

    assert isinstance(provider, TranslationProvider)
    assert provider.provider_name == "mock"


def test_result_keeps_translation_and_reverse_translation_separate() -> None:
    result = TranslationResult(
        translated_text="翻訳されたテキスト",
        detected_source_language=Language.ENGLISH,
        reverse_translation="Reverse translation",
        provider_metadata=ProviderMetadata(
            provider_name="mock",
            provider_mode=ProviderMode.MOCK,
        ),
    )

    assert result.translated_text != result.reverse_translation
    assert result.detected_source_language is Language.ENGLISH


def test_context_rejects_blank_or_duplicate_preservation_terms() -> None:
    with pytest.raises(ValidationError, match="must not be blank"):
        TranslationContext(preserve_terms=("",))

    with pytest.raises(ValidationError, match="must be unique"):
        TranslationContext(preserve_terms=("EQ-1048", "EQ-1048"))


def test_contracts_are_frozen_and_metadata_rejects_raw_payloads() -> None:
    context = TranslationContext(business_context="Manufacturing inspection")

    with pytest.raises(ValidationError, match="frozen"):
        context.business_context = "Changed"

    with pytest.raises(ValidationError, match="raw_payload"):
        ProviderMetadata.model_validate(
            {
                "provider_name": "mock",
                "provider_mode": "mock",
                "raw_payload": {"secret": "must-not-be-stored"},
            }
        )
