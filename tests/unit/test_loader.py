from unittest.mock import MagicMock

import pytest

from db.loader import CollectionLoader

LOADER_METHODS = [
    "LoadEmojis",
    "LoadEmoticons",
    "LoadArrows",
    "LoadMathSymbols",
    "LoadCurrency",
    "LoadSpecialSymbols",
    "LoadHieroglyphs",
    "LoadNerdFonts",
]

REQUIRED_SYMBOL_KEYS = {
    "id",
    "type",
    "symbol",
    "unicode",
    "name",
    "aliases",
    "category",
    "subcategory",
    "tags",
    "metadata",
}


@pytest.fixture
def loader(monkeypatch):
    # LoadNerdFonts calls notify_if_nerd_font_missing(app), which checks
    # installed fonts and may fire a real Gio.Notification if a nerd font
    # isn't installed on the test machine. Patch it so loader tests don't
    # depend on the runner's installed fonts.
    monkeypatch.setattr("db.loader.notify_if_nerd_font_missing", lambda app: None)
    return CollectionLoader(app=MagicMock())


@pytest.mark.parametrize("method_name", LOADER_METHODS)
def test_loader_returns_valid_structure(loader, method_name):
    method = getattr(loader, method_name)
    data = method()

    assert "categories" in data
    assert "symbols" in data
    assert isinstance(data["categories"], list)
    assert isinstance(data["symbols"], list)


@pytest.mark.parametrize("method_name", LOADER_METHODS)
def test_loader_symbols_have_required_keys(loader, method_name):
    method = getattr(loader, method_name)
    data = method()

    assert len(data["symbols"]) > 0, f"{method_name} loaded zero symbols"

    for entry in data["symbols"]:
        missing = REQUIRED_SYMBOL_KEYS - entry.keys()
        assert not missing, (
            f"{method_name} entry {entry.get('id')} missing keys: {missing}"
        )


# @pytest.mark.parametrize("method_name", LOADER_METHODS)
# def test_loader_symbol_ids_are_unique(loader, method_name):
#     method = getattr(loader, method_name)
#     data = method()

#     ids = [e["id"] for e in data["symbols"]]
#     duplicates = {i for i in ids if ids.count(i) > 1}
#     assert not duplicates, f"{method_name} has duplicate ids: {duplicates}"


@pytest.mark.parametrize("method_name", LOADER_METHODS)
def test_loader_symbol_field_types(loader, method_name):
    method = getattr(loader, method_name)
    data = method()

    for entry in data["symbols"]:
        assert isinstance(entry["symbol"], str) and entry["symbol"] != ""
        assert isinstance(entry["unicode"], list)
        assert isinstance(entry["aliases"], list)
        assert isinstance(entry["tags"], list)
        assert isinstance(entry["metadata"], dict)


@pytest.mark.parametrize("method_name", LOADER_METHODS)
def test_loader_categories_have_icon(loader, method_name):
    method = getattr(loader, method_name)
    data = method()

    for cat in data["categories"]:
        assert "icon" in cat
        assert "name" in cat


def test_load_nerd_fonts_calls_notification_hook(monkeypatch):
    called = []
    monkeypatch.setattr(
        "db.loader.notify_if_nerd_font_missing", lambda app: called.append(app)
    )
    app = MagicMock()
    loader = CollectionLoader(app)
    loader.LoadNerdFonts()
    assert called == [app]


def test_load_missing_file_raises(loader):
    with pytest.raises(FileNotFoundError):
        loader._load("does_not_exist.json")
