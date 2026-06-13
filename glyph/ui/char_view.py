import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib, Gdk
from utils.config import Config
from ui.side_bar import SideBar, COLLECTIONS
from ui.category_bar import CategoryBar
from ui.symbol_grid import SymbolGrid
from services.history import HistoryService

_config = Config()
_history = HistoryService()


class CharView(Gtk.Box):
    def __init__(self, parent, initial_data, loader_name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.parent = parent
        self.active_loader = loader_name
        self._config = _config
        self._history_active = False

        self.set_vexpand(True)
        self.set_hexpand(True)

        self.entries = initial_data
        self.active_category = None
        self.search_active = False

        self._process_entries()

        self.category_bar = CategoryBar(
            self.entries["categories"],
            on_category_change=self._on_category_changed,
            on_history_toggle=self._on_history_toggle,
        )
        self.append(self.category_bar)

        self.grid = SymbolGrid(on_symbol_clicked=self._on_symbol_clicked)
        self.append(self.grid)

        self.side_bar = SideBar(on_collection_change=self._on_collection_changed)
        self.side_bar.set_halign(Gtk.Align.END)
        self.side_bar.set_valign(Gtk.Align.FILL)
        self.side_bar.set_vexpand(True)

        self._refresh_grid()

    def _process_entries(self):
        for entry in self.entries["symbols"]:
            tags = " ".join(entry.get("tags", []))
            aliases = " ".join(entry.get("aliases", []))
            metadata = " ".join(str(v) for v in entry.get("metadata", {}).values())
            entry["search_text"] = (
                f"{entry.get('name', '')} {tags} {aliases} "
                f"{entry.get('category', '')} {entry.get('subcategory', '')} "
                f"{metadata}"
            ).lower()

        self.filtered_entries = list(self.entries["symbols"])

    def _refresh_grid(self):
        if self._history_active:
            self.grid.show_history(
                _history.get_global(), on_clear=self._on_history_cleared
            )
            return
        self.grid.refresh(self.filtered_entries)

    def _on_category_changed(self, category):
        self._history_active = False
        self.active_category = category
        if not self.search_active:
            self._apply_filter()

    def _apply_filter(self):
        symbols = self.entries["symbols"]
        if self.active_category:
            self.filtered_entries = [
                e for e in symbols if e.get("category") == self.active_category
            ]
        else:
            self.filtered_entries = list(symbols)
        self._refresh_grid()

    def filter_entries(self, query):
        text = query.strip().lower()
        self.search_active = bool(text)

        if text and self._history_active:
            self._history_active = False
            self.category_bar.deactivate_history()

        if text:
            self.filtered_entries = [
                e for e in self.entries["symbols"] if text in e["search_text"]
            ]
            self.grid.refresh(self.filtered_entries)
        else:
            self._apply_filter()

    def _on_history_toggle(self, active: bool):
        self._history_active = active
        if active:
            self.search_active = False
            self.grid.show_history(
                _history.get_global(), on_clear=self._on_history_cleared
            )
        else:
            self._apply_filter()

    def _on_history_cleared(self):
        _history.clear_global()
        self.grid.show_history([], on_clear=self._on_history_cleared)

    def toggle_history(self):
        self.category_bar.activate_history()

    def _on_collection_changed(self, data):
        self.entries = data
        self.active_category = None
        self.search_active = False
        self._history_active = False

        self._process_entries()
        self.category_bar.rebuild(self.entries["categories"])
        self.category_bar.deactivate_history()
        self._apply_filter()
        self.side_bar.set_reveal_child(False)

    def load_collection(self, loader_name):
        from db.loader import CollectionLoader

        method = getattr(CollectionLoader(), loader_name, None)
        if method:
            self.active_loader = loader_name
            self._on_collection_changed(method())

    def reload_current_collection(self):
        self.load_collection(self.active_loader)

    def _on_symbol_clicked(self, symbol):
        entry = next(
            (e for e in self.entries["symbols"] if e.get("symbol") == symbol),
            {"symbol": symbol},
        )

        _history.add(entry)

        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(symbol)

        if self._config.get("behavior", "show_notifications", default=True):
            notification = Gio.Notification.new("OmniGlyph")
            notification.set_body(f"Copied: {symbol}")
            app = self.parent.get_application()
            if app:
                app.send_notification(None, notification)

        if self._history_active:
            self.grid.show_history(
                _history.get_global(), on_clear=self._on_history_cleared
            )

        if self._config.get("behavior", "close_on_copy", default=True):
            GLib.timeout_add(100, lambda: (self.parent.hide(), False)[1])

    def scroll_by(self, delta):
        self.grid.scroll_by(delta)

    def copy_first_symbol(self):
        if self.filtered_entries:
            self._on_symbol_clicked(self.filtered_entries[0].get("symbol", ""))

    def select_next_category(self):
        self._step_category(+1)

    def select_prev_category(self):
        self._step_category(-1)

    def _step_category(self, direction):
        if self._history_active:
            return
        order = self.category_bar.get_order()
        if not order:
            return
        try:
            idx = order.index(self.active_category)
        except ValueError:
            idx = 0
        self.category_bar.select(order[(idx + direction) % len(order)])

    def toggle_side_bar(self):
        self.side_bar.toggle()
