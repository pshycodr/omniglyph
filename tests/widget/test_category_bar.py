import pytest

from ui.category_bar import CategoryBar


def make_categories():
    return [
        {"name": "Smileys", "icon": "😀"},
        {"name": "Animals", "icon": "🐶"},
    ]


@pytest.fixture
def bar():
    category_changes = []
    history_toggles = []
    return (
        CategoryBar(
            make_categories(),
            on_category_change=lambda c: category_changes.append(c),
            on_history_toggle=lambda a: history_toggles.append(a),
        ),
        category_changes,
        history_toggles,
    )


def test_all_button_active_by_default(bar):
    cb, _, _ = bar
    assert cb.category_buttons[None].get_active() is True


def test_order_includes_none_first(bar):
    cb, _, _ = bar
    order = cb.get_order()
    assert order[0] is None
    assert order[1:] == ["Smileys", "Animals"]


def test_selecting_category_fires_callback(bar):
    cb, changes, _ = bar
    cb.category_buttons["Smileys"].set_active(True)
    assert changes == ["Smileys"]


def test_selecting_category_deactivates_all_button(bar):
    cb, _, _ = bar
    cb.category_buttons["Smileys"].set_active(True)
    assert cb.category_buttons[None].get_active() is False


def test_history_toggle_fires_correct_callback(bar):
    cb, _, history_toggles = bar
    cb._history_btn.set_active(True)
    assert history_toggles == [True]


def test_untoggling_history_reactivates_all(bar):
    cb, _, history_toggles = bar
    cb._history_btn.set_active(True)
    cb._history_btn.set_active(False)
    assert cb.category_buttons[None].get_active() is True
    assert history_toggles == [True, False]


def test_selecting_category_deactivates_history(bar):
    cb, _, history_toggles = bar
    cb._history_btn.set_active(True)
    cb.category_buttons["Smileys"].set_active(True)
    assert cb._history_btn.get_active() is False


def test_rebuild_replaces_categories(bar):
    cb, _, _ = bar
    cb.rebuild([{"name": "Currency", "icon": "$"}])
    assert "Currency" in cb.category_buttons
    assert "Smileys" not in cb.category_buttons


def test_activate_history_toggles_on_then_off(bar):
    cb, _, history_toggles = bar
    cb.activate_history()
    assert cb._history_btn.get_active() is True
    cb.activate_history()
    assert cb._history_btn.get_active() is False
