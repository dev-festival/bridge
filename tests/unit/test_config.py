"""Tests for application settings and public configuration."""

from pytest import MonkeyPatch

from bridge_surface.config import Settings


def test_settings_have_safe_local_defaults() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "Bridge Surface"
    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"
    assert settings.debug is False
    assert settings.log_level == "INFO"


def test_public_config_is_an_explicit_allowlist(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BRIDGE_API_KEY", "must-not-leak")
    monkeypatch.setenv("BRIDGE_PASSWORD", "must-not-leak")

    serialized = Settings(_env_file=None).public_config().model_dump_json()  # type: ignore[call-arg]

    assert "Bridge Surface" in serialized
    assert "must-not-leak" not in serialized
    assert "api_key" not in serialized.lower()
    assert "password" not in serialized.lower()
