import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gtk4LayerShell", "1.0")

from importlib.resources import files

from gi.repository import Gdk, Gtk
from utils.config import Config

css_provider = Gtk.CssProvider()
css_data = files("styles").joinpath("style.css").read_bytes()
css_provider.load_from_data(css_data)
Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(),
    css_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_USER,
)

COLLECTION_FLAGS = {
    "emoji": "LoadEmojis",
    "emoticons": "LoadEmoticons",
    "arrows": "LoadArrows",
    "math": "LoadMathSymbols",
    "currency": "LoadCurrency",
    "special": "LoadSpecialSymbols",
    "hieroglyphs": "LoadHieroglyphs",
}

DEFAULT_COLLECTION = "LoadEmojis"
config = Config()
