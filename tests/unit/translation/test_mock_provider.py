"""Tests for deterministic mock translation behavior."""

import socket
from typing import cast

import pytest
from pytest import MonkeyPatch

from bridge_surface.translation import (
    EmptySourceTextError,
    InvalidLanguagePairError,
    Language,
    MockTranslationProvider,
    TranslationContext,
    UnsupportedLanguageError,
)
from bridge_surface.translation.fixtures import FIXTURES


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("source_language", "target_language", "source_attribute", "target_attribute"),
    [
        (Language.ENGLISH, Language.JAPANESE, "english_text", "japanese_text"),
        (Language.JAPANESE, Language.ENGLISH, "japanese_text", "english_text"),
    ],
)
async def test_fixture_translation_is_directional_and_not_an_echo(
    source_language: Language,
    target_language: Language,
    source_attribute: str,
    target_attribute: str,
) -> None:
    fixture = FIXTURES[0]
    source_text = cast(str, getattr(fixture, source_attribute))
    expected_translation = cast(str, getattr(fixture, target_attribute))

    result = await MockTranslationProvider().translate(
        source_text,
        source_language,
        target_language,
        TranslationContext(),
    )

    assert result.translated_text == expected_translation
    assert result.translated_text != source_text
    assert result.reverse_translation == source_text
    assert result.detected_source_language is source_language
    assert result.provider_metadata.provider_name == "mock"
    assert result.provider_metadata.fixture_id == fixture.fixture_id


@pytest.mark.anyio
async def test_fixture_preserves_required_identifiers_and_numeric_values() -> None:
    fixture = FIXTURES[0]

    result = await MockTranslationProvider().translate(
        fixture.english_text,
        Language.ENGLISH,
        Language.JAPANESE,
        TranslationContext(),
    )

    preserved = {item.term for item in result.preserved_terms}
    required = {"EQ-1048", "WO123456", "Drawing 22A-118", "0.05 mm"}
    assert preserved == required
    assert all(term in result.translated_text for term in required)


@pytest.mark.anyio
async def test_repeated_translation_is_byte_for_byte_deterministic() -> None:
    fixture = FIXTURES[1]
    provider = MockTranslationProvider()
    context = TranslationContext(business_context="Downtime review")

    first = await provider.translate(
        fixture.japanese_text,
        Language.JAPANESE,
        Language.ENGLISH,
        context,
    )
    second = await provider.translate(
        fixture.japanese_text,
        Language.JAPANESE,
        Language.ENGLISH,
        context,
    )

    assert first == second
    assert first.model_dump_json() == second.model_dump_json()


@pytest.mark.anyio
async def test_unknown_text_uses_labeled_fallback_and_preserves_detected_terms() -> None:
    source = "Inspect EQ-1048 at 0.05 mm and record the result in IsoQuest."

    result = await MockTranslationProvider().translate(
        source,
        Language.ENGLISH,
        Language.JAPANESE,
        TranslationContext(preserve_terms=("IsoQuest",)),
    )

    assert result.translated_text.startswith("【モック翻訳(英語→日本語)】")
    assert result.translated_text != source
    assert result.reverse_translation.startswith("[MOCK reverse translation to English]")
    assert result.reverse_translation != result.translated_text
    assert {item.term for item in result.preserved_terms} == {
        "EQ-1048",
        "0.05 mm",
        "IsoQuest",
    }
    assert [warning.code for warning in result.warnings] == ["mock_fallback"]
    assert result.provider_metadata.fixture_id is None


@pytest.mark.anyio
async def test_japanese_fallback_has_a_distinct_direction_label() -> None:
    source = "設備の状態を確認してください。"

    result = await MockTranslationProvider().translate(
        source,
        Language.JAPANESE,
        Language.ENGLISH,
        TranslationContext(),
    )

    assert result.translated_text == f"[MOCK translation (Japanese→English)] {source}"
    assert result.reverse_translation == f"【モック逆翻訳(日本語)】{source}"


@pytest.mark.anyio
async def test_invalid_text_and_language_pairs_fail_clearly() -> None:
    provider = MockTranslationProvider()
    context = TranslationContext()

    with pytest.raises(EmptySourceTextError, match="must not be blank"):
        await provider.translate("  ", Language.ENGLISH, Language.JAPANESE, context)

    with pytest.raises(InvalidLanguagePairError, match="must be different"):
        await provider.translate("Text", Language.ENGLISH, Language.ENGLISH, context)

    with pytest.raises(UnsupportedLanguageError, match="source language"):
        await provider.translate(
            "Text",
            cast(Language, "fr"),
            Language.ENGLISH,
            context,
        )

    with pytest.raises(UnsupportedLanguageError, match="target language"):
        await provider.translate(
            "Text",
            Language.ENGLISH,
            cast(Language, "fr"),
            context,
        )


@pytest.mark.anyio
async def test_mock_translation_performs_no_network_access(monkeypatch: MonkeyPatch) -> None:
    def reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("The mock provider attempted network access.")

    monkeypatch.setattr(socket, "create_connection", reject_network)

    result = await MockTranslationProvider().translate(
        "Unknown local text",
        Language.ENGLISH,
        Language.JAPANESE,
        TranslationContext(),
    )

    assert result.provider_metadata.provider_name == "mock"
