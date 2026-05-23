import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


def create_search_bar():
    search = Gtk.SearchEntry()

    search.set_placeholder_text("Search symbols...")

    search.connect("search-changed", on_search_changed)

    return search


def on_search_changed(search):
    text = search.get_text()

    print(text)
