import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gtk4LayerShell", "1.0")

from gi.repository import Gtk, Adw
from gi.repository import Gtk4LayerShell


import os
from ui import *


class AppWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._setup_overlay_window()
        self._add_escape_close()
        self._build_layout()

        self.char_view = CharView(self)
        self.main_box.append(self.char_view)

    def _setup_overlay_window(self):
        is_wayland = os.environ.get("XDG_SESSION_TYPE") == "wayland"

        if not is_wayland:
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
        self.set_default_size(450, 600)

        self.main_box.set_spacing(10)

        self.set_content(self.main_box)

        header_bar = AppHeader()
        self.main_box.append(header_bar)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(12)
        box.set_margin_end(12)

        search = create_search_bar()

        search.set_hexpand(True)
        search.set_halign(Gtk.Align.FILL)

        box.append(search)

        self.main_box.append(box)

    def _add_escape_close(self):
        controller = Gtk.EventControllerKey()

        def on_key(_, keyval, *_args):
            # Esc key
            if keyval == 65307:
                self.close()
                return True

            return False

        controller.connect(
            "key-pressed",
            on_key,
        )

        self.add_controller(controller)


class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="dev.anishroy.glyph")

    def do_activate(self):
        window = AppWindow(self)
        window.present()


app = MyApp()
app.run()
