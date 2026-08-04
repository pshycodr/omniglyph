import json

import pytest
import utils.settings as settings_mod


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    monkeypatch.setattr(settings_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(settings_mod, "SETTINGS_FILE", tmp_path / "settings.json")
    return tmp_path


def test_load_creates_defaults_when_missing(isolated_settings):
    result = settings_mod.load_settings()
    assert result == settings_mod.DEFAULT_SETTINGS
    assert (isolated_settings / "settings.json").exists()


def test_get_setting_returns_default(isolated_settings):
    assert settings_mod.get_setting("hide_nerd_font_notification") is False


def test_set_setting_persists(isolated_settings):
    settings_mod.set_setting("hide_nerd_font_notification", True)
    assert settings_mod.get_setting("hide_nerd_font_notification") is True


def test_set_setting_preserves_other_keys(isolated_settings):
    settings_mod.set_setting("dismissed_update_version", "1.2.0")
    settings_mod.set_setting("hide_nerd_font_notification", True)

    data = json.loads((isolated_settings / "settings.json").read_text())
    assert data["dismissed_update_version"] == "1.2.0"
    assert data["hide_nerd_font_notification"] is True


def test_load_settings_survives_corrupt_json(isolated_settings):
    (isolated_settings / "settings.json").write_text("{not valid json")
    result = settings_mod.load_settings()
    assert result == settings_mod.DEFAULT_SETTINGS
