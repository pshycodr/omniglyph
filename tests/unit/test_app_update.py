import json
from unittest.mock import MagicMock, patch

import pytest

from services.notification.app_update import _parse_version, _check_for_updates


def test_parse_version_strips_v_prefix():
    assert _parse_version("v1.1.0") == (1, 1, 0)


def test_parse_version_no_prefix():
    assert _parse_version("2.0.3") == (2, 0, 3)


def test_parse_version_comparable():
    assert _parse_version("2.0.3") < _parse_version("2.1.0")
    assert _parse_version("1.9.9") < _parse_version("1.10.0")


def test_check_for_updates_notifies_on_newer_version(monkeypatch):
    monkeypatch.setattr(
        "services.notification.app_update.get_setting", lambda key: None
    )
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"tag_name": "v9.9.9"}).encode()
    fake_response.__enter__.return_value = fake_response

    with patch("urllib.request.urlopen", return_value=fake_response):
        with patch("gi.repository.GLib.idle_add") as idle_add:
            app = MagicMock()
            _check_for_updates(app)
            idle_add.assert_called_once()


def test_check_for_updates_skips_dismissed_version(monkeypatch):
    monkeypatch.setattr(
        "services.notification.app_update.get_setting", lambda key: "9.9.9"
    )
    fake_response = MagicMock()
    fake_response.read.return_value = json.dumps({"tag_name": "v9.9.9"}).encode()
    fake_response.__enter__.return_value = fake_response

    with patch("urllib.request.urlopen", return_value=fake_response):
        with patch("gi.repository.GLib.idle_add") as idle_add:
            app = MagicMock()
            _check_for_updates(app)
            idle_add.assert_not_called()


def test_check_for_updates_swallows_network_errors():
    with patch("urllib.request.urlopen", side_effect=OSError("no network")):
        _check_for_updates(MagicMock())  # must not raise
