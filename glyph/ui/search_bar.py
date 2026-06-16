import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gdk, Gtk
from utils.config import Config

_config = Config()


def create_search_bar(on_change=None):
    search = Gtk.SearchEntry()

    search_keybind = _config.shortcut_label("focus_search")
    print(search_keybind)
    search.set_placeholder_text(f"Press '{search_keybind}' to search | Esc to clear")

    def on_search_changed(widget):
        if on_change:
            on_change(widget.get_text())

    def on_key_pressed(controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            root = search.get_root()

            if root:
                root.set_focus(None)

            return True

        return False

    controller = Gtk.EventControllerKey()

    controller.connect(
        "key-pressed",
        on_key_pressed,
    )

    search.add_controller(controller)

    search.connect(
        "search-changed",
        on_search_changed,
    )

    return search
