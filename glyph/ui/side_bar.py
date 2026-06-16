import gi

gi.require_version("Gtk", "4.0")

from db.loader import CollectionLoader
from gi.repository import Gtk
from utils.config import Config

COLLECTIONS = [
    {
        "name": "Emoji",
        "icon": "😀",
        "loader": "LoadEmojis",
    },
    {
        "name": "Emoticons",
        "icon": ":-)",
        "loader": "LoadEmoticons",
    },
    {
        "name": "Arrows",
        "icon": "↔",
        "loader": "LoadArrows",
    },
    {
        "name": "Math",
        "icon": "∑",
        "loader": "LoadMathSymbols",
    },
    {
        "name": "Currency",
        "icon": "$",
        "loader": "LoadCurrency",
    },
    {
        "name": "Special",
        "icon": "!",
        "loader": "LoadSpecialSymbols",
    },
    {
        "name": "Nerd-Font Icons",
        "icon": "",
        "loader": "LoadNerdFonts",
    },
    {
        "name": "Hieroglyphs",
        "icon": "𓂀",
        "loader": "LoadHieroglyphs",
    },
]

_config = Config()


class SideBar(Gtk.Revealer):
    def __init__(self, app, on_collection_change=None):
        super().__init__()

        self.app = app
        self._config = _config
        self.on_collection_change = on_collection_change
        self._active_btn = None
        self._ignore_toggle = False

        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.set_transition_duration(200)
        self.set_reveal_child(False)
        self.set_valign(Gtk.Align.FILL)
        self.set_vexpand(True)

        sidebar_width = self._config.get("behavior", "sidebar_width", default=180)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.add_css_class("sidebar")
        outer.set_size_request(sidebar_width, -1)
        outer.set_vexpand(True)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_top(12)
        header.set_margin_bottom(8)
        header.set_margin_start(12)
        header.set_margin_end(12)

        title = Gtk.Label(label="Collections")
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)
        title.add_css_class("heading")

        close_sc = self._config.shortcut_label("close_sidebar")
        close_btn = Gtk.Button()
        close_btn.set_icon_name("window-close-symbolic")
        close_btn.set_valign(Gtk.Align.CENTER)
        close_btn.add_css_class("flat")
        close_btn.set_tooltip_text(f"Close sidebar ({close_sc})")
        close_btn.connect("clicked", lambda _: self.toggle())

        header.append(title)
        header.append(close_btn)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        list_box.set_margin_top(8)
        list_box.set_margin_bottom(8)
        list_box.set_margin_start(8)
        list_box.set_margin_end(8)

        self._buttons = {}

        toggle_sc = self._config.shortcut_label("toggle_sidebar")

        for collection in COLLECTIONS:
            btn = Gtk.ToggleButton()
            btn.add_css_class("sidebar-item")
            btn.set_hexpand(True)
            btn.set_tooltip_text(
                f"Switch to {collection['name']} ({toggle_sc} to toggle sidebar)"
            )

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_margin_top(6)
            row.set_margin_bottom(6)
            row.set_margin_start(8)
            row.set_margin_end(8)

            icon_label = Gtk.Label(label=collection["icon"])
            icon_label.set_halign(Gtk.Align.START)
            icon_label.set_size_request(28, -1)

            name_label = Gtk.Label(label=collection["name"])
            name_label.set_halign(Gtk.Align.START)
            name_label.set_hexpand(True)
            name_label.add_css_class("body")

            row.append(icon_label)
            row.append(name_label)
            btn.set_child(row)

            btn.connect("toggled", self._on_item_toggled, collection)
            list_box.append(btn)

            self._buttons[collection["name"]] = btn

        first_name = COLLECTIONS[0]["name"]
        self._ignore_toggle = True
        self._buttons[first_name].set_active(True)
        self._active_btn = self._buttons[first_name]
        self._ignore_toggle = False

        scroll.set_child(list_box)

        outer.append(header)
        outer.append(sep)
        outer.append(scroll)

        self.set_child(outer)

    def _on_item_toggled(self, btn, collection):
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
        self._ignore_toggle = False

        self._load_collection(collection)

    def _load_collection(self, collection):
        loader = CollectionLoader(self.app)
        method = getattr(loader, collection["loader"])
        data = method()

        if self.on_collection_change:
            self.on_collection_change(data)

    def toggle(self):
        self.set_reveal_child(not self.get_reveal_child())

    def is_open(self):
        return self.get_reveal_child()
