import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gio, GLib, Gdk

from db.loader import CollectionLoader
from ui.side_bar import SideBar

BATCH_SIZE = 30
SCROLL_THRESHOLD = 0.85


class CharView(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.parent = parent

        self.set_vexpand(True)
        self.set_hexpand(True)

        self.entries = []
        self.filtered_entries = []
        self.categories = []
        self.active_category = None
        self.search_active = False
        self._ignore_toggle = False

        self._load_database()
        self._build_category_bar()
        self._build_scroll_area()

        self.side_bar = SideBar(on_collection_change=self._on_collection_changed)
        self.side_bar.set_halign(Gtk.Align.END)
        self.side_bar.set_valign(Gtk.Align.FILL)
        self.side_bar.set_vexpand(True)

        self._refresh_grid()

    def _load_database(self):
        self.entries = CollectionLoader().LoadEmojis()
        self._process_entries()

    def _process_entries(self):
        seen_categories = []
        category_counts = {}

        for entry in self.entries["symbols"]:
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

            if category not in seen_categories:
                seen_categories.append(category)

            category_counts[category] = category_counts.get(category, 0) + 1

        self.categories = self.entries["categories"]
        self.category_counts = category_counts
        self.filtered_entries = list(self.entries["symbols"])

    def _build_category_bar(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.set_hexpand(True)

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        bar.set_margin_top(6)
        bar.set_margin_bottom(6)
        bar.set_margin_start(8)
        bar.set_margin_end(8)

        self.category_buttons = {}

        all_btn = Gtk.ToggleButton()
        all_btn.set_label("All")
        all_btn.set_active(True)
        all_btn.add_css_class("category-pill")
        all_btn.connect("toggled", self._on_category_toggled, None)
        bar.append(all_btn)
        self.category_buttons[None] = all_btn

        for category in self.categories:
            category_name = category["name"]
            category_icon = category["icon"]

            btn = Gtk.ToggleButton()
            btn.set_label(category_icon)
            btn.set_tooltip_text(category_name)
            btn.add_css_class("category-pill")
            btn.connect("toggled", self._on_category_toggled, category_name)
            bar.append(btn)

            self.category_buttons[category_name] = btn

        scroll.set_child(bar)
        self.append(scroll)
        self._active_btn = all_btn

    def _on_category_toggled(self, btn, category):
        if self._ignore_toggle:
            return

        if not btn.get_active():
            if self._active_btn is btn:
                self._ignore_toggle = True
                btn.set_active(True)
                self._ignore_toggle = False
            return

        self._ignore_toggle = True

        if self._active_btn and self._active_btn is not btn:
            self._active_btn.set_active(False)

        self._active_btn = btn
        self.active_category = category

        self._ignore_toggle = False

        if not self.search_active:
            self._apply_filter()

    def _build_scroll_area(self):
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vadj = self.scroll.get_vadjustment()
        vadj.connect("value-changed", self._on_scroll)

        self.content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
        )

        self.scroll.set_child(self.content_box)
        self.append(self.scroll)

        self.section_widgets = {}

    def _on_collection_changed(self, data):
        self.entries = data
        self.active_category = None
        self.search_active = False

        self._process_entries()
        self._rebuild_category_bar()
        self._apply_filter()

        self.side_bar.set_reveal_child(False)

    def _rebuild_category_bar(self):
        self._ignore_toggle = True

        self.category_buttons = {}

        category_scroll = None
        child = self.get_first_child()
        while child:
            if isinstance(child, Gtk.ScrolledWindow):
                category_scroll = child
                break
            child = child.get_next_sibling()

        if category_scroll is None:
            self._ignore_toggle = False
            return

        viewport = category_scroll.get_child()
        bar = viewport.get_child() if isinstance(viewport, Gtk.Viewport) else viewport

        while True:
            first = bar.get_first_child()
            if first is None:
                break
            bar.remove(first)

        all_btn = Gtk.ToggleButton()
        all_btn.set_label("All")
        all_btn.set_active(True)
        all_btn.add_css_class("category-pill")
        all_btn.connect("toggled", self._on_category_toggled, None)
        bar.append(all_btn)
        self.category_buttons[None] = all_btn
        self._active_btn = all_btn

        for category in self.categories:
            category_name = category["name"]
            category_icon = category["icon"]

            btn = Gtk.ToggleButton()
            btn.set_label(category_icon)
            btn.set_tooltip_text(category_name)
            btn.add_css_class("category-pill")
            btn.connect("toggled", self._on_category_toggled, category_name)
            bar.append(btn)

            self.category_buttons[category_name] = btn

        self._ignore_toggle = False

    def toggle_side_bar(self):
        self.side_bar.toggle()

    def filter_entries(self, query):
        text = query.strip().lower()

        self.search_active = bool(text)

        symbols = self.entries["symbols"]

        if text:
            self.filtered_entries = [
                entry for entry in symbols if text in entry["search_text"]
            ]
        else:
            self._apply_filter()
            return

        self._refresh_grid()

    def _apply_filter(self):
        symbols = self.entries["symbols"]

        if self.active_category:
            self.filtered_entries = [
                entry
                for entry in symbols
                if entry.get("category") == self.active_category
            ]
        else:
            self.filtered_entries = list(symbols)

        self._refresh_grid()

    def _refresh_grid(self):
        while True:
            child = self.content_box.get_first_child()
            if child is None:
                break
            self.content_box.remove(child)

        self.section_widgets = {}
        self.render_index = 0
        self.loading = False

        self._load_next_batch()

    def _get_sections(self):
        sections = {}
        order = []
        for entry in self.filtered_entries:
            cat = entry.get("category", "Other")
            if cat not in sections:
                sections[cat] = []
                order.append(cat)
            sections[cat].append(entry)
        return order, sections

    def _ensure_section(self, category, total):
        if category in self.section_widgets:
            return self.section_widgets[category]["grid"]

        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        section_box.set_margin_top(12)
        section_box.set_margin_bottom(4)
        section_box.set_margin_start(12)
        section_box.set_margin_end(12)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_hexpand(True)

        name_label = Gtk.Label(label=category)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        name_label.add_css_class("heading")

        count_label = Gtk.Label(label=str(total))
        count_label.set_halign(Gtk.Align.END)
        count_label.add_css_class("dim-label")

        header.append(name_label)
        header.append(count_label)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(4)

        grid = Gtk.FlowBox()
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_max_children_per_line(13)
        grid.set_row_spacing(2)
        grid.set_column_spacing(2)
        grid.set_homogeneous(True)

        section_box.append(header)
        section_box.append(sep)
        section_box.append(grid)

        self.content_box.append(section_box)
        self.section_widgets[category] = {"box": section_box, "grid": grid}

        return grid

    def _load_next_batch(self):
        if self.loading:
            return

        self.loading = True

        batch = self.filtered_entries[
            self.render_index : self.render_index + BATCH_SIZE
        ]

        order, all_sections = self._get_sections()

        for entry in batch:
            category = entry.get("category", "Other")
            total = len(all_sections.get(category, []))
            grid = self._ensure_section(category, total)
            self._add_symbol_button(entry, grid)

        self.render_index += len(batch)
        self.loading = False

    def _add_symbol_button(self, entry, grid):
        symbol = entry.get("symbol", "")

        button = Gtk.Button()
        button.add_css_class("symbol-button")
        button.set_size_request(60, 60)
        button.connect("clicked", self._on_symbol_clicked, symbol)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        char_label = Gtk.Label()
        char_label.set_markup(
            f"<span font='20'>{GLib.markup_escape_text(symbol)}</span>"
        )

        box.append(char_label)
        button.set_child(box)
        button.set_tooltip_text(entry.get("name", ""))

        grid.append(button)

    def _on_symbol_clicked(self, button, symbol):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(symbol)

        notification = Gio.Notification.new("OmniGlyph")
        notification.set_body(f"Copied: {symbol}")

        app = self.parent.get_application()
        if app:
            app.send_notification(None, notification)

        GLib.timeout_add(100, self.close_window)

    def close_window(self):
        self.parent.hide()
        return False

    def _on_scroll(self, adjustment):
        upper = adjustment.get_upper()
        page_size = adjustment.get_page_size()
        value = adjustment.get_value()

        if upper <= page_size:
            return

        position = (value + page_size) / upper

        if position >= SCROLL_THRESHOLD and self.render_index < len(
            self.filtered_entries
        ):
            self._load_next_batch()
