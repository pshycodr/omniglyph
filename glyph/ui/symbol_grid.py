from gi.repository import GLib, Gtk
from utils.config import Config

SCROLL_THRESHOLD = 0.85
_config = Config()


class SymbolGrid(Gtk.Box):
    def __init__(self, on_symbol_clicked):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self._on_symbol_clicked = on_symbol_clicked

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.get_vadjustment().connect("value-changed", self._on_scroll)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.scroll.set_child(self.content_box)
        self.append(self.scroll)

        self.section_widgets = {}
        self.render_index = 0
        self.loading = False
        self.filtered_entries = []

    def _batch_size(self):
        return _config.get("behavior", "batch_size", default=30)

    def _grid_columns(self):
        return _config.get("behavior", "grid_columns", default=13)

    def refresh(self, entries):
        self.filtered_entries = entries

        while child := self.content_box.get_first_child():
            self.content_box.remove(child)

        self.section_widgets = {}
        self.render_index = 0
        self.loading = False

        self._load_next_batch()

    def scroll_by(self, delta):
        vadj = self.scroll.get_vadjustment()
        new_val = max(
            vadj.get_lower(),
            min(vadj.get_upper() - vadj.get_page_size(), vadj.get_value() + delta),
        )
        vadj.set_value(new_val)

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
        grid.set_max_children_per_line(self._grid_columns())
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
            self.render_index : self.render_index + self._batch_size()
        ]
        _, all_sections = self._get_sections()

        for entry in batch:
            category = entry.get("category", "Other")
            total = len(all_sections.get(category, []))
            grid = self._ensure_section(category, total)
            self._add_symbol_button(entry, grid)

        self.render_index += len(batch)
        self.loading = False

    def _add_symbol_button(self, entry, grid):
        symbol = entry.get("symbol", "")
        copy_sc = _config.shortcut_label("copy_first")

        button = Gtk.Button()
        button.add_css_class("symbol-button")
        button.set_size_request(60, 60)
        button.connect("clicked", lambda _, s=symbol: self._on_symbol_clicked(s))

        char_label = Gtk.Label()
        char_label.set_markup(
            f"<span font='20'>{GLib.markup_escape_text(symbol)}</span>"
        )

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.append(char_label)
        button.set_child(box)

        name = entry.get("name", "")
        if self.filtered_entries and self.filtered_entries[0] is entry:
            button.set_tooltip_text(f"{name} — click or {copy_sc} to copy")
        else:
            button.set_tooltip_text(name)

        grid.append(button)

    def _on_scroll(self, adjustment):
        upper = adjustment.get_upper()
        page_size = adjustment.get_page_size()
        value = adjustment.get_value()

        if upper <= page_size:
            return

        if (value + page_size) / upper >= SCROLL_THRESHOLD:
            if self.render_index < len(self.filtered_entries):
                self._load_next_batch()
