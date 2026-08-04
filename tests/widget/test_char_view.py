from unittest.mock import MagicMock

import pytest
from ui.char_view import CharView


@pytest.fixture
def mock_loader(monkeypatch):
    fake_cls = MagicMock()
    fake_cls.return_value.LoadEmojis.return_value = {"symbols": [], "categories": []}
    monkeypatch.setattr("ui.side_bar.CollectionLoader", fake_cls)
    return fake_cls


def make_entries():
    return {
        "symbols": [
            {
                "symbol": "😀",
                "name": "grinning face",
                "category": "Smileys",
                "tags": ["happy", "joy"],
            },
            {
                "symbol": "🐶",
                "name": "dog face",
                "category": "Animals",
                "tags": ["pet"],
            },
        ],
        "categories": [
            {"name": "Smileys", "icon": "😀"},
            {"name": "Animals", "icon": "🐶"},
        ],
    }


@pytest.fixture
def char_view(mock_loader):
    parent = MagicMock()
    return CharView(
        parent=parent,
        initial_data=make_entries(),
        loader_name="LoadEmojis",
        app=MagicMock(),
    )


def test_process_entries_builds_search_text(char_view):
    entry = char_view.entries["symbols"][0]
    assert "grinning face" in entry["search_text"]
    assert "happy" in entry["search_text"]
    assert "smileys" in entry["search_text"]


def test_initial_filtered_entries_is_all_symbols(char_view):
    assert len(char_view.filtered_entries) == 2


def test_filter_entries_matches_tag(char_view):
    char_view.filter_entries("happy")
    assert len(char_view.filtered_entries) == 1
    assert char_view.filtered_entries[0]["symbol"] == "😀"


def test_filter_entries_empty_query_restores_all(char_view):
    char_view.filter_entries("happy")
    char_view.filter_entries("")
    assert len(char_view.filtered_entries) == 2


def test_filter_entries_sets_search_active(char_view):
    char_view.filter_entries("dog")
    assert char_view.search_active is True
    char_view.filter_entries("")
    assert char_view.search_active is False


def test_category_change_filters_entries(char_view):
    char_view._on_category_changed("Animals")
    assert len(char_view.filtered_entries) == 1
    assert char_view.filtered_entries[0]["symbol"] == "🐶"


def test_category_change_ignored_while_searching(char_view):
    char_view.search_active = True
    char_view._on_category_changed("Animals")
    # active_category is still updated, but _apply_filter is skipped
    assert char_view.active_category == "Animals"


def test_step_category_wraps_forward(char_view):
    order = char_view.category_bar.get_order()
    char_view.category_bar.select(order[-1])
    char_view.select_next_category()
    assert char_view.active_category == order[0]


def test_step_category_noop_during_history(char_view):
    char_view._history_active = True
    original = char_view.active_category
    char_view.select_next_category()
    assert char_view.active_category == original


def test_copy_first_symbol_uses_first_filtered_entry(char_view, monkeypatch):
    clicked = []
    monkeypatch.setattr(char_view, "_on_symbol_clicked", lambda s: clicked.append(s))
    char_view.copy_first_symbol()
    assert clicked == ["😀"]


def test_history_toggle_shows_history(char_view, monkeypatch):
    monkeypatch.setattr("ui.char_view._history.get_global", lambda: [{"symbol": "🐶"}])
    char_view._on_history_toggle(True)
    assert char_view._history_active is True


def test_on_symbol_clicked_adds_to_history_and_copies(char_view, monkeypatch):
    added = []
    monkeypatch.setattr("ui.char_view._history.add", lambda e: added.append(e))
    char_view._on_symbol_clicked("😀")
    assert added[0]["symbol"] == "😀"


def test_reload_current_collection_calls_load_collection(char_view, monkeypatch):
    called = []
    monkeypatch.setattr(char_view, "load_collection", lambda name: called.append(name))
    char_view.active_loader = "LoadMathSymbols"
    char_view.reload_current_collection()
    assert called == ["LoadMathSymbols"]


def test_load_collection_uses_real_loader(char_view, monkeypatch):
    fake_loader = MagicMock()
    fake_loader.LoadArrows.return_value = {"symbols": [], "categories": []}
    monkeypatch.setattr("db.loader.CollectionLoader", lambda: fake_loader)
    char_view.load_collection("LoadArrows")
    assert char_view.active_loader == "LoadArrows"
