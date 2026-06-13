import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk
from utils.config import Config

_config = Config()


class CategoryBar(Gtk.ScrolledWindow):
    def __init__(self, categories, on_category_change, on_history_toggle):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.set_hexpand(True)

        self._on_category_change = on_category_change
        self._on_history_toggle = on_history_toggle
        self._ignore_toggle = False
        self._active_btn = None
        self._history_btn = None
        self.category_buttons = {}
        self._category_order = []

        self._bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self._bar.set_margin_top(6)
        self._bar.set_margin_bottom(6)
        self._bar.set_margin_start(8)
        self._bar.set_margin_end(8)
        self.set_child(self._bar)

        self.rebuild(categories)

    def rebuild(self, categories):
        self._ignore_toggle = True

        self.category_buttons = {}
        self._category_order = [None]

        while child := self._bar.get_first_child():
            self._bar.remove(child)

        next_sc = _config.shortcut_label("next_category")
        prev_sc = _config.shortcut_label("prev_category")

        self._history_btn = Gtk.ToggleButton()
        self._history_btn.set_icon_name("document-open-recent-symbolic")
        self._history_btn.set_tooltip_text("History (Ctrl+H)")
        self._history_btn.add_css_class("category-pill")
        self._history_btn.connect("toggled", self._on_history_toggled)
        self._bar.append(self._history_btn)

        all_btn = Gtk.ToggleButton()
        all_btn.set_label("All")
        all_btn.set_active(True)
        all_btn.add_css_class("category-pill")
        all_btn.set_tooltip_text(f"All categories ({prev_sc} / {next_sc} to navigate)")
        all_btn.connect("toggled", self._on_category_toggled, None)
        self._bar.append(all_btn)
        self.category_buttons[None] = all_btn
        self._active_btn = all_btn

        for category in categories:
            name = category["name"]
            icon = category["icon"]

            btn = Gtk.ToggleButton()
            btn.set_label(icon)
            btn.set_tooltip_text(f"{name} ({prev_sc} / {next_sc} to navigate)")
            btn.add_css_class("category-pill")
            btn.connect("toggled", self._on_category_toggled, name)
            self._bar.append(btn)

            self.category_buttons[name] = btn
            self._category_order.append(name)

        self._ignore_toggle = False

    def _on_history_toggled(self, btn):
        if self._ignore_toggle:
            return

        if btn.get_active():
            self._ignore_toggle = True
            if self._active_btn:
                self._active_btn.set_active(False)
                self._active_btn = None
            self._ignore_toggle = False
            self._on_history_toggle(True)
        else:
            self._ignore_toggle = True
            all_btn = self.category_buttons.get(None)
            if all_btn:
                all_btn.set_active(True)
                self._active_btn = all_btn
            self._ignore_toggle = False
            self._on_history_toggle(False)

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

        if self._history_btn and self._history_btn.get_active():
            self._history_btn.set_active(False)

        if self._active_btn and self._active_btn is not btn:
            self._active_btn.set_active(False)

        self._active_btn = btn
        self._ignore_toggle = False

        self._on_category_change(category)

    def select(self, category):
        btn = self.category_buttons.get(category)
        if btn:
            btn.set_active(True)

    def activate_history(self):
        if not self._history_btn.get_active():
            self._history_btn.set_active(True)
        else:
            self._history_btn.set_active(False)

    def deactivate_history(self):
        if self._history_btn and self._history_btn.get_active():
            self._history_btn.set_active(False)

    def get_order(self):
        return self._category_order
