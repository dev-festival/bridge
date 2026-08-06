"""Tests for translation provider construction."""

import pytest
from pytest import MonkeyPatch

from bridge_surface.translation import (
    MockTranslationProvider,
    TranslationProvider,
    UnsupportedProviderError,
    create_translation_provider,
)


def test_factory_defaults_to_mock_without_configuration_or_credentials(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.delenv("TRANSLATION_PROVIDER", raising=False)
    monkeypatch.delenv("TRANSLATION_API_KEY", raising=False)

    provider = create_translation_provider()

    assert isinstance(provider, MockTranslationProvider)
    assert isinstance(provider, TranslationProvider)
    assert provider.provider_name == "mock"


def test_factory_accepts_explicit_mock_name() -> None:
    assert isinstance(create_translation_provider(" MOCK "), MockTranslationProvider)


def test_factory_rejects_unimplemented_provider() -> None:
    with pytest.raises(UnsupportedProviderError, match="Unsupported translation provider"):
        create_translation_provider("real-provider")
