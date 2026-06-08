import gi

from utils.window_manager import is_tiling_window_manager

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk, Adw, Gdk, Gio
from gi.repository import Gtk4LayerShell

import os
from ui import *


class AppWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        setup_actions(self)

        self._setup_overlay_window()

        self.char_view = CharView(self)

        self._build_layout()
        self._setup_keyboard_shortcuts()

        self.main_box.append(self.char_view)

        self.connect(
            "close-request",
            self._on_close_request,
        )

    def _on_close_request(self, *_):
        self.set_visible(False)
        return True

    def _hide_window(self):
        self.set_visible(False)

    def show_and_focus(self):
        self.search.set_text("")

        self.char_view.filter_entries("")

        self.present()

        self._focus_search()

    def _setup_overlay_window(self):
        if not is_tiling_window_manager():
            return

        self.set_decorated(False)
        self.set_resizable(False)

        Gtk4LayerShell.init_for_window(self)

        Gtk4LayerShell.set_layer(
            self,
            Gtk4LayerShell.Layer.OVERLAY,
        )

        Gtk4LayerShell.set_keyboard_mode(
            self,
            Gtk4LayerShell.KeyboardMode.EXCLUSIVE,
        )

        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.TOP,
            True,
        )

        Gtk4LayerShell.set_anchor(
            self,
            Gtk4LayerShell.Edge.RIGHT,
            True,
        )

        Gtk4LayerShell.set_margin(
            self,
            Gtk4LayerShell.Edge.TOP,
            20,
        )

        Gtk4LayerShell.set_margin(
            self,
            Gtk4LayerShell.Edge.RIGHT,
            20,
        )

    def _build_layout(self):
        self.set_title("OmniGlyph")

        if not is_tiling_window_manager():
            appHeader = AppHeader()
            self.main_box.append(appHeader)

        self.set_default_size(
            450,
            500,
        )

        self.main_box.set_spacing(0)

        self.set_content(self.main_box)

        search_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        search_box.set_margin_top(12)
        search_box.set_margin_bottom(8)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)

        self.search = create_search_bar(on_change=self.char_view.filter_entries)

        self.search.set_hexpand(True)

        self.search.set_halign(Gtk.Align.FILL)

        search_box.append(self.search)

        self.main_box.append(search_box)

    def _setup_keyboard_shortcuts(self):
        controller = Gtk.EventControllerKey()

        controller.connect(
            "key-pressed",
            self._on_key_pressed,
        )

        self.add_controller(controller)

    def _focus_search(self):
        self.search.grab_focus()

        self.search.select_region(
            0,
            len(self.search.get_text()),
        )

    def _on_key_pressed(
        self,
        controller,
        keyval,
        keycode,
        state,
    ):
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

    def do_activate(self):
        if self.window is None:
            self.window = AppWindow(self)

            self.hold()

        self.window.show_and_focus()

    def do_command_line(
        self,
        command_line,
    ):
        self.activate()

        return 0


app = MyApp()
app.run()
