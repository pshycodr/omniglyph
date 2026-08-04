# tests/unit/test_window.py
from unittest.mock import MagicMock

import pytest
from gi.repository import Gdk

from window import AppWindow


@pytest.fixture
def mock_loader(monkeypatch):
    fake_cls = MagicMock()
    fake_cls.return_value.LoadEmojis.return_value = {"symbols": [], "categories": []}
    monkeypatch.setattr("ui.side_bar.CollectionLoader", fake_cls)
    return fake_cls


@pytest.fixture
def app_window(mock_loader, monkeypatch, gtk_app):
    monkeypatch.setattr("window.is_tiling_window_manager", lambda: False)
    initial_data = {"symbols": [], "categories": []}
    return AppWindow(gtk_app, initial_data, "LoadEmojis")


def test_window_title_set(app_window):
    assert app_window.get_title() == "OmniGlyph"


def test_close_request_hides_instead_of_destroying(app_window):
    result = app_window._on_close_request()
    assert result is True
    assert app_window.get_visible() is False


def test_match_returns_false_for_unmatched_key(app_window):
    keyval = Gdk.KEY_a
    mods = Gdk.ModifierType(0)
    assert app_window._match(keyval, mods, "quit", "ctrl+q") is False


def test_match_returns_true_for_matched_key(app_window):
    keyval = Gdk.KEY_q
    mods = Gdk.ModifierType.CONTROL_MASK
    assert app_window._match(keyval, mods, "quit", "ctrl+q") is True


def test_match_case_insensitive_keyval(app_window):
    keyval = Gdk.KEY_Q  # uppercase keyval
    mods = Gdk.ModifierType.CONTROL_MASK
    assert app_window._match(keyval, mods, "quit", "ctrl+q") is True


def test_match_returns_false_when_no_shortcut_configured(app_window, monkeypatch):
    monkeypatch.setattr(app_window.config, "get", lambda *a, **kw: "")
    assert app_window._match(Gdk.KEY_q, Gdk.ModifierType(0), "quit") is False


def test_on_key_pressed_quit_calls_close(app_window, monkeypatch):
    closed = []
    monkeypatch.setattr(app_window, "_close_window", lambda: closed.append(True))
    monkeypatch.setattr(app_window, "get_focus", lambda: None)

    result = app_window._on_key_pressed(
        None, Gdk.KEY_q, 0, Gdk.ModifierType.CONTROL_MASK
    )

    assert result is True
    assert closed == [True]


def test_on_key_pressed_escape_hides_when_not_search_focused(app_window, monkeypatch):
    hidden = []
    monkeypatch.setattr(app_window, "_hide_window", lambda: hidden.append(True))
    monkeypatch.setattr(app_window, "get_focus", lambda: None)

    result = app_window._on_key_pressed(None, Gdk.KEY_Escape, 0, Gdk.ModifierType(0))

    assert result is True
    assert hidden == [True]


def test_on_key_pressed_escape_unfocuses_search_when_focused(app_window, monkeypatch):
    monkeypatch.setattr(app_window, "get_focus", lambda: app_window.search)
    unfocused = []
    monkeypatch.setattr(app_window, "set_focus", lambda w: unfocused.append(w))

    result = app_window._on_key_pressed(None, Gdk.KEY_Escape, 0, Gdk.ModifierType(0))

    assert result is True
    assert unfocused == [None]


def test_on_key_pressed_next_category_skipped_when_search_focused(
    app_window, monkeypatch
):
    monkeypatch.setattr(app_window, "get_focus", lambda: app_window.search)
    called = []
    monkeypatch.setattr(
        app_window.char_view, "select_next_category", lambda: called.append(True)
    )

    app_window._on_key_pressed(None, Gdk.KEY_l, 0, Gdk.ModifierType(0))

    assert called == []


def test_on_key_pressed_next_category_fires_when_not_search_focused(
    app_window, monkeypatch
):
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    called = []
    monkeypatch.setattr(
        app_window.char_view, "select_next_category", lambda: called.append(True)
    )

    result = app_window._on_key_pressed(None, Gdk.KEY_l, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [True]


def test_on_key_pressed_sidebar_open_intercepts_navigation(app_window, monkeypatch):
    monkeypatch.setattr(app_window.char_view.side_bar, "is_open", lambda: True)
    called = []
    monkeypatch.setattr(
        app_window.char_view.side_bar,
        "select_next_collection",
        lambda: called.append(True),
    )

    result = app_window._on_key_pressed(None, Gdk.KEY_j, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [True]


def test_on_key_pressed_sidebar_open_ignores_unmapped_keys(app_window, monkeypatch):
    monkeypatch.setattr(app_window.char_view.side_bar, "is_open", lambda: True)

    result = app_window._on_key_pressed(None, Gdk.KEY_a, 0, Gdk.ModifierType(0))

    assert result is False


def test_on_key_pressed_reload_collection(app_window, monkeypatch):
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    called = []
    monkeypatch.setattr(
        app_window.char_view, "reload_current_collection", lambda: called.append(True)
    )

    result = app_window._on_key_pressed(
        None, Gdk.KEY_r, 0, Gdk.ModifierType.CONTROL_MASK
    )

    assert result is True
    assert called == [True]


def test_focus_search_selects_all_text(app_window):
    app_window.search.set_text("hello")
    app_window._focus_search()
    start, end = app_window.search.get_selection_bounds()
    assert (start, end) == (0, 5)


def test_on_key_pressed_copy_first(app_window, monkeypatch):
    called = []
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    monkeypatch.setattr(
        app_window.char_view, "copy_first_symbol", lambda: called.append(True)
    )

    result = app_window._on_key_pressed(None, Gdk.KEY_Return, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [True]


def test_on_key_pressed_prev_category(app_window, monkeypatch):
    called = []
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    monkeypatch.setattr(
        app_window.char_view, "select_prev_category", lambda: called.append(True)
    )

    result = app_window._on_key_pressed(None, Gdk.KEY_h, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [True]


def test_on_key_pressed_scroll_down(app_window, monkeypatch):
    called = []
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    monkeypatch.setattr(app_window.char_view, "scroll_by", lambda d: called.append(d))

    result = app_window._on_key_pressed(None, Gdk.KEY_j, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [120]


def test_on_key_pressed_scroll_up(app_window, monkeypatch):
    called = []
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    monkeypatch.setattr(app_window.char_view, "scroll_by", lambda d: called.append(d))

    result = app_window._on_key_pressed(None, Gdk.KEY_k, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [-120]


def test_on_key_pressed_history_shortcut(app_window, monkeypatch):
    called = []
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    monkeypatch.setattr(
        app_window.char_view, "toggle_history", lambda: called.append(True)
    )

    result = app_window._on_key_pressed(
        None, Gdk.KEY_h, 0, Gdk.ModifierType.CONTROL_MASK
    )

    assert result is True
    assert called == [True]


def test_on_key_pressed_sidebar_close_via_return(app_window, monkeypatch):
    monkeypatch.setattr(app_window.char_view.side_bar, "is_open", lambda: True)
    toggled = []
    monkeypatch.setattr(
        app_window.char_view, "toggle_side_bar", lambda: toggled.append(True)
    )

    result = app_window._on_key_pressed(None, Gdk.KEY_Return, 0, Gdk.ModifierType(0))

    assert result is True
    assert toggled == [True]


def test_on_key_pressed_sidebar_toggle_while_open(app_window, monkeypatch):
    monkeypatch.setattr(app_window.char_view.side_bar, "is_open", lambda: True)
    toggled = []
    monkeypatch.setattr(
        app_window.char_view, "toggle_side_bar", lambda: toggled.append(True)
    )

    result = app_window._on_key_pressed(
        None, Gdk.KEY_b, 0, Gdk.ModifierType.CONTROL_MASK
    )

    assert result is True
    assert toggled == [True]


def test_on_key_pressed_sidebar_prev_selection(app_window, monkeypatch):
    monkeypatch.setattr(app_window.char_view.side_bar, "is_open", lambda: True)
    called = []
    monkeypatch.setattr(
        app_window.char_view.side_bar,
        "select_prev_collection",
        lambda: called.append(True),
    )

    result = app_window._on_key_pressed(None, Gdk.KEY_k, 0, Gdk.ModifierType(0))

    assert result is True
    assert called == [True]


def test_on_key_pressed_escape_quits_when_esc_action_quit(app_window, monkeypatch):
    monkeypatch.setattr(app_window, "get_focus", lambda: None)
    monkeypatch.setattr(
        app_window.config,
        "get",
        lambda *a, **kw: "quit"
        if a[:2] == ("behavior", "esc_action")
        else kw.get("default"),
    )
    closed = []
    monkeypatch.setattr(app_window, "_close_window", lambda: closed.append(True))

    result = app_window._on_key_pressed(None, Gdk.KEY_Escape, 0, Gdk.ModifierType(0))

    assert result is True
    assert closed == [True]
