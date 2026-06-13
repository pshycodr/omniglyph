import sys

import gi
from window import AppWindow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gtk4LayerShell", "1.0")


from constants import *
from db.loader import CollectionLoader
from gi.repository import Adw, Gio
from ui import *
from services.notification import *


class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=APP_ID,
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
        print("DO ACTIVATE")
        setup_update_notifications(self)
        check_for_updates_async(self)

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

        self.do_activate()
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
