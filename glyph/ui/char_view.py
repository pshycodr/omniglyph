import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib, Gdk

from db.loader import CollectionLoader


class CharView(Gtk.ScrolledWindow):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.set_vexpand(True)
        self.set_hexpand(True)

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
        )

        self.set_child(self.box)

        self.entries = []
        self.filtered_entries = []

        self.active_category = None

        self.render_index = 0
        self.loading = False

        self._build_grid()
        self._load_database()
        self._render_entries()

    def _build_grid(self):
        self.scroll = Gtk.ScrolledWindow()

        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)

        vadj = self.scroll.get_vadjustment()

        vadj.connect("value-changed", self.on_scroll)

        self.grid = Gtk.FlowBox()

        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)

        self.grid.set_max_children_per_line(13)

        self.grid.set_row_spacing(8)
        self.grid.set_column_spacing(8)

        self.scroll.set_child(self.grid)

        self.box.append(self.scroll)

    def _load_database(self):
        self.entries = CollectionLoader().LoadEmojis()

        category_counts = {}

        for entry in self.entries:
            tags = " ".join(entry.get("tags", []))

            aliases = " ".join(entry.get("aliases", []))

            metadata = " ".join([str(v) for v in entry.get("metadata", {}).values()])

            entry["search_text"] = (
                f"{entry.get('name', '')} "
                f"{tags} "
                f"{aliases} "
                f"{entry.get('category', '')} "
                f"{entry.get('subcategory', '')} "
                f"{metadata}"
            ).lower()

            category = entry.get("category", "Other")

            category_counts[category] = category_counts.get(category, 0) + 1

        self.category_counts = category_counts

    def _render_entries(self):
        for entry in self.entries:
            self._add_symbol_button(entry)

    def _add_symbol_button(self, entry):
        symbol = entry.get("symbol", "")

        button = Gtk.Button()

        button.set_size_request(72, 72)

        button.connect("clicked", self._on_symbol_clicked, symbol)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )

        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        char_label = Gtk.Label()

        char_label.set_markup(
            f"<span font='24'>{GLib.markup_escape_text(symbol)}</span>"
        )

        box.append(char_label)

        button.set_child(box)

        tooltip = f"{entry.get('name', '')}\n"

        button.set_tooltip_text(tooltip)

        self.grid.append(button)

    def _on_symbol_clicked(self, button, symbol):
        clipboard = Gdk.Display.get_default().get_clipboard()

        clipboard.set_text(symbol)

        notification = Gio.Notification.new("OmniGlyph")

        notification.set_body(f"Copied: {symbol}")

        app = self.parent.get_application()

        if app:
            app.send_notification(None, notification)

        GLib.timeout_add(100, self.close_window)

    def close_window(self):
        self.parent.close()
        return False

    def on_scroll(self, adjustment):
        pass
