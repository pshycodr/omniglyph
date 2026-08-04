from unittest.mock import MagicMock

import pytest

from ui.side_bar import COLLECTIONS, SideBar


@pytest.fixture
def mock_loader(monkeypatch):
    fake_loader_cls = MagicMock()
    fake_instance = fake_loader_cls.return_value
    fake_instance.LoadEmojis.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadEmoticons.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadArrows.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadMathSymbols.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadCurrency.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadSpecialSymbols.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadNerdFonts.return_value = {"symbols": [], "categories": []}
    fake_instance.LoadHieroglyphs.return_value = {"symbols": [], "categories": []}
    monkeypatch.setattr("ui.side_bar.CollectionLoader", fake_loader_cls)
    return fake_loader_cls


@pytest.fixture
def side_bar(mock_loader):
    changes = []
    sb = SideBar(app=MagicMock(), on_collection_change=lambda d: changes.append(d))
    sb.changes = changes
    return sb


def test_first_collection_active_on_init(side_bar):
    first_name = COLLECTIONS[0]["name"]
    assert side_bar._active_btn is side_bar._buttons[first_name]


def test_construction_does_not_trigger_load(side_bar, mock_loader):
    mock_loader.return_value.LoadEmojis.assert_not_called()


def test_switching_collection_calls_correct_loader(side_bar, mock_loader):
    side_bar._buttons["Arrows"].set_active(True)
    mock_loader.return_value.LoadArrows.assert_called_once()


def test_switching_collection_fires_callback(side_bar):
    side_bar._buttons["Math"].set_active(True)
    assert len(side_bar.changes) == 1


def test_switching_deactivates_previous_button(side_bar):
    first_name = COLLECTIONS[0]["name"]
    side_bar._buttons["Currency"].set_active(True)
    assert side_bar._buttons[first_name].get_active() is False


def test_clicking_active_button_stays_active(side_bar):
    first_name = COLLECTIONS[0]["name"]
    btn = side_bar._buttons[first_name]
    btn.set_active(False)
    assert btn.get_active() is True


def test_toggle_reveals_and_hides(side_bar):
    assert side_bar.is_open() is False
    side_bar.toggle()
    assert side_bar.is_open() is True
    side_bar.toggle()
    assert side_bar.is_open() is False


def test_select_next_collection_wraps(side_bar):
    names = [c["name"] for c in COLLECTIONS]
    last_name = names[-1]
    side_bar._buttons[last_name].set_active(True)
    side_bar.select_next_collection()
    assert side_bar._active_btn is side_bar._buttons[names[0]]


def test_select_prev_collection(side_bar):
    names = [c["name"] for c in COLLECTIONS]
    side_bar.select_prev_collection()
    assert side_bar._active_btn is side_bar._buttons[names[-1]]
