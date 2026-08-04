from unittest.mock import MagicMock, patch

from services.notification.nerd_font import (
    has_nerd_font,
    notify_if_nerd_font_missing,
    setup_nerd_font_actions,
)


def test_has_nerd_font_true_when_family_present():
    fake_family = MagicMock()
    fake_family.get_name.return_value = "JetBrainsMono Nerd Font"
    fake_fontmap = MagicMock()
    fake_fontmap.list_families.return_value = [fake_family]

    with patch(
        "gi.repository.PangoCairo.FontMap.get_default", return_value=fake_fontmap
    ):
        assert has_nerd_font() is True


def test_has_nerd_font_false_when_absent():
    fake_family = MagicMock()
    fake_family.get_name.return_value = "Sans"
    fake_fontmap = MagicMock()
    fake_fontmap.list_families.return_value = [fake_family]

    with patch(
        "gi.repository.PangoCairo.FontMap.get_default", return_value=fake_fontmap
    ):
        assert has_nerd_font() is False


def test_has_nerd_font_swallows_exceptions():
    with patch(
        "gi.repository.PangoCairo.FontMap.get_default", side_effect=Exception("boom")
    ):
        assert has_nerd_font() is False


def test_notify_skipped_when_font_present(monkeypatch):
    monkeypatch.setattr("services.notification.nerd_font.has_nerd_font", lambda: True)
    app = MagicMock()
    notify_if_nerd_font_missing(app)
    app.send_notification.assert_not_called()


def test_notify_skipped_when_dismissed(monkeypatch):
    monkeypatch.setattr("services.notification.nerd_font.has_nerd_font", lambda: False)
    monkeypatch.setattr("services.notification.nerd_font.get_setting", lambda key: True)
    app = MagicMock()
    notify_if_nerd_font_missing(app)
    app.send_notification.assert_not_called()


def test_notify_fires_when_font_missing_and_not_dismissed(monkeypatch):
    monkeypatch.setattr("services.notification.nerd_font.has_nerd_font", lambda: False)
    monkeypatch.setattr(
        "services.notification.nerd_font.get_setting", lambda key: False
    )
    app = MagicMock()
    notify_if_nerd_font_missing(app)
    app.send_notification.assert_called_once()


def test_setup_nerd_font_actions_registers_two_actions():
    app = MagicMock()
    setup_nerd_font_actions(app)
    assert app.add_action.call_count == 2


def test_setup_nerd_font_actions_swallows_exceptions():
    app = MagicMock()
    app.add_action.side_effect = Exception("boom")
    setup_nerd_font_actions(app)  # must not raise
