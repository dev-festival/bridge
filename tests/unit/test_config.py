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
    assert settings.database_url == "sqlite:///./bridge_surface.db"
    assert str(settings.local_user_id) == "00000000-0000-4000-8000-000000000001"
    assert settings.local_user_display_name == "Local User"
    assert settings.local_user_preferred_language == "en"
    assert "database_url" not in repr(settings)


def test_public_config_is_an_explicit_allowlist(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BRIDGE_API_KEY", "must-not-leak")
    monkeypatch.setenv("BRIDGE_PASSWORD", "must-not-leak")

    serialized = Settings(_env_file=None).public_config().model_dump_json()  # type: ignore[call-arg]

    assert "Bridge Surface" in serialized
    assert "must-not-leak" not in serialized
    assert "api_key" not in serialized.lower()
    assert "password" not in serialized.lower()
    assert "database" not in serialized.lower()
    assert "local_user" not in serialized.lower()


def test_database_url_can_be_configured_from_the_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BRIDGE_DATABASE_URL", "sqlite:///./configured.db")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.database_url == "sqlite:///./configured.db"


def test_local_user_can_be_configured_from_the_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BRIDGE_LOCAL_USER_ID", "11111111-1111-4111-8111-111111111111")
    monkeypatch.setenv("BRIDGE_LOCAL_USER_DISPLAY_NAME", "Configured Owner")
    monkeypatch.setenv("BRIDGE_LOCAL_USER_PREFERRED_LANGUAGE", "ja")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert str(settings.local_user_id) == "11111111-1111-4111-8111-111111111111"
    assert settings.local_user_display_name == "Configured Owner"
    assert settings.local_user_preferred_language == "ja"
