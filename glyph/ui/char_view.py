from gi.repository import Gdk, Gio, GLib, Gtk
from utils.config import Config

from ui.category_bar import CategoryBar
from ui.side_bar import SideBar
from ui.symbol_grid import SymbolGrid

_config = Config()


class CharView(Gtk.Box):
    def __init__(self, parent, initial_data, loader_name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.parent = parent
        self.active_loader = loader_name
        self._config = _config

        self.set_vexpand(True)
        self.set_hexpand(True)

        self.entries = initial_data
        self.active_category = None
        self.search_active = False

        self._process_entries()

        self.category_bar = CategoryBar(
            self.entries["categories"],
            on_category_change=self._on_category_changed,
        )
        self.append(self.category_bar)

        self.grid = SymbolGrid(on_symbol_clicked=self._on_symbol_clicked)
        self.append(self.grid)

        self.side_bar = SideBar(on_collection_change=self._on_collection_changed)
        self.side_bar.set_halign(Gtk.Align.END)
        self.side_bar.set_valign(Gtk.Align.FILL)
        self.side_bar.set_vexpand(True)

        self.grid.refresh(self.filtered_entries)

    def _process_entries(self):
        for entry in self.entries["symbols"]:
            tags = " ".join(entry.get("tags", []))
            aliases = " ".join(entry.get("aliases", []))
            metadata = " ".join(str(v) for v in entry.get("metadata", {}).values())
            entry["search_text"] = (
                f"{entry.get('name', '')} {tags} {aliases} "
                f"{entry.get('category', '')} {entry.get('subcategory', '')} {metadata}"
            ).lower()

        self.filtered_entries = list(self.entries["symbols"])

    def _on_category_changed(self, category):
        self.active_category = category
        if not self.search_active:
            self._apply_filter()

    def _on_collection_changed(self, data):
        self.entries = data
        self.active_category = None
        self.search_active = False

        self._process_entries()
        self.category_bar.rebuild(self.entries["categories"])
        self._apply_filter()
        self.side_bar.set_reveal_child(False)

    def _apply_filter(self):
        symbols = self.entries["symbols"]
        if self.active_category:
            self.filtered_entries = [
                e for e in symbols if e.get("category") == self.active_category
            ]
        else:
            self.filtered_entries = list(symbols)
        self.grid.refresh(self.filtered_entries)

    def filter_entries(self, query):
        text = query.strip().lower()
        self.search_active = bool(text)

        if text:
            self.filtered_entries = [
                e for e in self.entries["symbols"] if text in e["search_text"]
            ]
            self.grid.refresh(self.filtered_entries)
        else:
            self._apply_filter()

    def _on_symbol_clicked(self, symbol):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(symbol)

        if self._config.get("behavior", "show_notifications", default=True):
            notification = Gio.Notification.new("OmniGlyph")
            notification.set_body(f"Copied: {symbol}")
            app = self.parent.get_application()
            if app:
                app.send_notification(None, notification)

        if self._config.get("behavior", "close_on_copy", default=True):
            GLib.timeout_add(100, lambda: (self.parent.hide(), False)[1])

    # --- delegated to grid ---
    def scroll_by(self, delta):
        self.grid.scroll_by(delta)

    def copy_first_symbol(self):
        if self.filtered_entries:
            self._on_symbol_clicked(self.filtered_entries[0].get("symbol", ""))

    # --- delegated to category_bar ---
    def select_next_category(self):
        order = self.category_bar.get_order()
        self._step_category(order, +1)

    def select_prev_category(self):
        order = self.category_bar.get_order()
        self._step_category(order, -1)

    def _step_category(self, order, direction):
        if not order:
            return
        try:
            idx = order.index(self.active_category)
        except ValueError:
            idx = 0
        self.category_bar.select(order[(idx + direction) % len(order)])

    # --- delegated to side_bar ---
    def toggle_side_bar(self):
        self.side_bar.toggle()

    # --- collection loading ---
    def load_collection(self, loader_name):
        from db.loader import CollectionLoader

        method = getattr(CollectionLoader(), loader_name, None)
        if method:
            self._on_collection_changed(method())

    def reload_current_collection(self):
        self.load_collection(self.active_loader)
