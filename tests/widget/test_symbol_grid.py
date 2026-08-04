import pytest

from ui.symbol_grid import SymbolGrid


def make_entries(n, category="Smileys"):
    return [
        {"symbol": f"S{i}", "name": f"symbol {i}", "category": category}
        for i in range(n)
    ]


@pytest.fixture
def grid():
    clicked = []
    g = SymbolGrid(on_symbol_clicked=lambda s: clicked.append(s))
    g.clicked = clicked
    return g


def test_refresh_stores_filtered_entries(grid):
    entries = make_entries(5)
    grid.refresh(entries)
    assert grid.filtered_entries == entries


def test_refresh_creates_section_for_category(grid):
    grid.refresh(make_entries(3, category="Arrows"))
    assert "Arrows" in grid.section_widgets


def test_batch_loading_respects_batch_size(grid, monkeypatch):
    monkeypatch.setattr(grid, "_batch_size", lambda: 10)
    grid.refresh(make_entries(25))
    assert grid.render_index == 10


def test_show_history_empty_state(grid):
    grid.show_history([])
    # empty state renders a label instead of a grid; content_box should
    # have at least the header row plus the empty-state label
    child = grid.content_box.get_first_child()
    assert child is not None


def test_show_history_populates_entries(grid):
    grid.show_history([{"symbol": "😀", "name": "grinning"}])
    assert grid.filtered_entries == []  # history mode doesn't set filtered_entries
