import gi
import sys

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk, Adw, Gdk, Gio
from gi.repository import Gtk4LayerShell

from ui import *
from db.loader import CollectionLoader

from utils.window_manager import is_tiling_window_manager
from importlib.resources import files

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


class AppWindow(Adw.ApplicationWindow):
    def __init__(self, app, initial_data, loader_name):
        super().__init__(application=app)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        setup_actions(self)

        self._setup_overlay_window()

        self.char_view = CharView(self, initial_data, loader_name)

        self._build_layout()
        self._setup_keyboard_shortcuts()

        self.main_box.append(self.char_view)

        self.connect("close-request", self._on_close_request)

    def _on_close_request(self, *_):
        self.set_visible(False)
        return True

    def _hide_window(self):
        self.set_visible(False)

    def show_and_focus(self, data, loader_name):
        self.search.set_text("")

        if loader_name != self.char_view.active_loader:
            self.char_view._on_collection_changed(data)
            self.char_view.active_loader = loader_name

        self.present()

        self._focus_search()

    def _setup_overlay_window(self):
        if not is_tiling_window_manager():
            return

        self.set_decorated(False)
        self.set_resizable(False)

        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.EXCLUSIVE)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.TOP, 20)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.RIGHT, 20)

    def _build_layout(self):
        self.set_title("OmniGlyph")

        if not is_tiling_window_manager():
            self.main_box.append(AppHeader())

        self.set_default_size(450, 500)
        self.main_box.set_spacing(0)

        self.root_overlay = Gtk.Overlay()
        self.root_overlay.set_child(self.main_box)
        self.set_content(self.root_overlay)

        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.set_margin_top(12)
        search_box.set_margin_bottom(8)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)

        self.search = create_search_bar(on_change=self.char_view.filter_entries)
        self.search.set_hexpand(True)
        self.search.set_halign(Gtk.Align.FILL)

        side_bar_button = Gtk.Button()
        side_bar_button.set_icon_name("open-menu-symbolic")
        side_bar_button.set_valign(Gtk.Align.START)
        side_bar_button.set_tooltip_text("Open sidebar")
        side_bar_button.set_margin_start(6)
        side_bar_button.connect("clicked", lambda _: self.char_view.toggle_side_bar())

        search_box.append(self.search)
        search_box.append(side_bar_button)

        self.main_box.append(search_box)
        self.root_overlay.add_overlay(self.char_view.side_bar)

    def _setup_keyboard_shortcuts(self):
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

    def _focus_search(self):
        self.search.grab_focus()
        self.search.select_region(0, len(self.search.get_text()))

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_slash:
            self._focus_search()
            return True

        if keyval != Gdk.KEY_Escape:
            return False

        if self.get_focus() is self.search:
            self.set_focus(None)
            return True

        self._hide_window()
        return True


class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.anishroy.omniglyph",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.window = None

    def _resolve_collection(self, args):
        for arg in args:
            flag = arg.lstrip("-").lower()
            if flag in COLLECTION_FLAGS:
                return COLLECTION_FLAGS[flag]
        return DEFAULT_COLLECTION

    def _load(self, loader_name):
        return getattr(CollectionLoader(), loader_name)()

    def do_activate(self):
        pass

    def do_command_line(self, command_line):
        raw = command_line.get_arguments()[1:]
        args = [a.decode() if isinstance(a, bytes) else a for a in raw]

        for arg in args:
            flag = arg.lstrip("-").lower()
            if flag in ("help", "h"):
                flags = "\n  ".join(f"--{f}" for f in COLLECTION_FLAGS)
                print(
                    f"Usage: omniglyph [OPTION]\n\nCollections:\n  {flags}\n\nDefault: --emoji"
                )
                return 0

        loader_name = self._resolve_collection(args)

        if self.window is None:
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.DEFAULT)
            data = self._load(loader_name)
            self.window = AppWindow(self, data, loader_name)
            self.hold()
            self.window.show_and_focus(data, loader_name)
        else:
            if loader_name != self.window.char_view.active_loader:
                data = self._load(loader_name)
                self.window.show_and_focus(data, loader_name)
            else:
                self.window.show_and_focus(None, loader_name)

        return 0


app = MyApp()
app.run(sys.argv)
