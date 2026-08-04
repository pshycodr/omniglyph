from unittest.mock import MagicMock

import pytest
from main import MyApp


@pytest.fixture
def app():
    return MyApp()


def test_resolve_collection_defaults_to_emoji(app):
    assert app._resolve_collection([]) == "LoadEmojis"


def test_resolve_collection_matches_known_flag(app):
    assert app._resolve_collection(["--math"]) == "LoadMathSymbols"


def test_resolve_collection_case_insensitive(app):
    assert app._resolve_collection(["--MATH"]) == "LoadMathSymbols"


def test_resolve_collection_strips_leading_dashes(app):
    assert app._resolve_collection(["-math"]) == "LoadMathSymbols"
    assert app._resolve_collection(["math"]) == "LoadMathSymbols"


def test_resolve_collection_ignores_unknown_flags(app):
    assert app._resolve_collection(["--bogus"]) == "LoadEmojis"


def test_resolve_collection_first_match_wins(app):
    assert (
        app._resolve_collection(["--bogus", "--currency", "--math"]) == "LoadCurrency"
    )


def test_load_delegates_to_collection_loader(app, monkeypatch):
    fake_loader_cls = MagicMock()
    fake_loader_cls.return_value.LoadMathSymbols.return_value = {
        "symbols": [],
        "categories": [],
    }
    monkeypatch.setattr("main.CollectionLoader", fake_loader_cls)

    result = app._load("LoadMathSymbols")

    fake_loader_cls.return_value.LoadMathSymbols.assert_called_once()
    assert result == {"symbols": [], "categories": []}


def test_command_line_help_flag_returns_zero_without_creating_window(
    app, monkeypatch, capsys
):
    command_line = MagicMock()
    command_line.get_arguments.return_value = ["omniglyph", "--help"]

    result = app.do_command_line(command_line)

    assert result == 0
    assert app.window is None
    captured = capsys.readouterr()
    assert "Usage: omniglyph" in captured.out


def test_command_line_short_help_flag(app):
    command_line = MagicMock()
    command_line.get_arguments.return_value = ["omniglyph", "-h"]

    result = app.do_command_line(command_line)

    assert result == 0
    assert app.window is None


def test_command_line_creates_window_on_first_call(app, monkeypatch):
    command_line = MagicMock()
    command_line.get_arguments.return_value = ["omniglyph"]

    monkeypatch.setattr(app, "do_activate", lambda: None)
    monkeypatch.setattr(app, "_load", lambda name: {"symbols": [], "categories": []})
    monkeypatch.setattr(app, "hold", lambda: None)

    fake_window_cls = MagicMock()
    monkeypatch.setattr("main.AppWindow", fake_window_cls)

    result = app.do_command_line(command_line)

    assert result == 0
    fake_window_cls.assert_called_once()
    fake_window_cls.return_value.show_and_focus.assert_called_once()


def test_command_line_reuses_window_same_collection(app, monkeypatch):
    command_line = MagicMock()
    command_line.get_arguments.return_value = ["omniglyph"]

    fake_window = MagicMock()
    fake_window.char_view.active_loader = "LoadEmojis"
    app.window = fake_window

    monkeypatch.setattr(app, "do_activate", lambda: None)
    load_mock = MagicMock()
    monkeypatch.setattr(app, "_load", load_mock)

    app.do_command_line(command_line)

    load_mock.assert_not_called()
    fake_window.show_and_focus.assert_called_once_with(None, "LoadEmojis")


def test_command_line_reloads_window_different_collection(app, monkeypatch):
    command_line = MagicMock()
    command_line.get_arguments.return_value = ["omniglyph", "--math"]

    fake_window = MagicMock()
    fake_window.char_view.active_loader = "LoadEmojis"
    app.window = fake_window

    monkeypatch.setattr(app, "do_activate", lambda: None)
    monkeypatch.setattr(app, "_load", lambda name: {"symbols": [], "categories": []})

    app.do_command_line(command_line)

    fake_window.show_and_focus.assert_called_once_with(
        {"symbols": [], "categories": []}, "LoadMathSymbols"
    )


def test_command_line_decodes_byte_arguments(app, monkeypatch):
    command_line = MagicMock()
    command_line.get_arguments.return_value = ["omniglyph", b"--math"]

    fake_window = MagicMock()
    fake_window.char_view.active_loader = "LoadEmojis"
    app.window = fake_window

    monkeypatch.setattr(app, "do_activate", lambda: None)
    monkeypatch.setattr(app, "_load", lambda name: {})

    app.do_command_line(command_line)

    fake_window.show_and_focus.assert_called_once_with({}, "LoadMathSymbols")
