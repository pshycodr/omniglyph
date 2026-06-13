import json
from pathlib import Path

from gi.repository import GLib

DEFAULT_CONFIG = {
    "shortcuts": {
        "quit": "ctrl+q",
        "focus_search": "slash",
        "toggle_categories": "c",
        "toggle_sidebar": "s",
        "close_sidebar": "escape",
        "next_category": "]",
        "prev_category": "[",
        "sidebar_next": "down",
        "sidebar_prev": "up",
        "sidebar_activate": "return",
        "copy_first": "ctrl+return",
        "scroll_down": "j",
        "scroll_up": "k",
        "reload_collection": "ctrl+r",
    },
    "behavior": {
        "esc_action": "hide",
        "theme": "system",
        "close_on_copy": True,
        "show_notifications": True,
        "grid_columns": 13,
        "batch_size": 30,
        "window_width": 450,
        "window_height": 500,
        "sidebar_width": 180,
        "scroll_step": 120,
    },
}

_KEY_DISPLAY = {
    "slash": "/",
    "escape": "Esc",
    "return": "Enter",
    "enter": "Enter",
    "right": "→",
    "left": "←",
    "up": "↑",
    "down": "↓",
    "tab": "Tab",
    "space": "Space",
    "backspace": "Backspace",
    "delete": "Del",
    "home": "Home",
    "end": "End",
    "pageup": "PgUp",
    "pagedown": "PgDn",
}


class Config:
    def __init__(self):
        config_dir = Path(GLib.get_user_config_dir()) / "omniglyph"
        config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = config_dir / "config.json"

        if not self.config_file.exists():
            self.save(DEFAULT_CONFIG)

        self.data = self._load_with_defaults()

    def _load_with_defaults(self):
        try:
            with open(self.config_file, "r") as f:
                user_data = json.load(f)
        except Exception:
            return self._deep_copy(DEFAULT_CONFIG)

        return self._merge(self._deep_copy(DEFAULT_CONFIG), user_data)

    def _deep_copy(self, d):
        return json.loads(json.dumps(d))

    def _merge(self, base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge(base[key], value)
            else:
                base[key] = value
        return base

    def load(self):
        return self._load_with_defaults()

    def save(self, data):
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)

    def get(self, *keys, default=None):
        value = self.data

        for key in keys:
            if not isinstance(value, dict):
                return default

            value = value.get(key)

            if value is None:
                return default

        return value

    def shortcut_label(self, name):
        raw = self.get("shortcuts", name, default="")
        if not raw:
            return ""
        parts = raw.split("+")
        result = []
        for p in parts:
            pl = p.lower()
            if pl in ("ctrl", "shift", "alt", "super"):
                result.append(pl.capitalize())
            else:
                result.append(
                    _KEY_DISPLAY.get(pl, p.upper() if len(p) == 1 else p.capitalize())
                )
        return "+".join(result)
