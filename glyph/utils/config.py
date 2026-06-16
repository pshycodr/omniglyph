from copy import deepcopy
from pathlib import Path
import tomllib

from gi.repository import GLib

DEFAULT_CONFIG = r"""
# OmniGlyph Configuration
#
# Location:
# ~/.config/omniglyph/config.toml
#
# Restart OmniGlyph after changing this file.
#
# ---------------------------------------------------------------------------
# Shortcut Syntax
# ---------------------------------------------------------------------------
#
# A shortcut is composed of zero or more modifiers followed by a key:
#
#   ctrl+q
#   ctrl+shift+h
#   alt+s
#   super+space
#   ctrl+alt+delete
#
# Modifiers:
#   ctrl, shift, alt, super
#
# Navigation Keys:
#   up, down, left, right
#   home, end
#   pageup, pagedown
#
# Editing Keys:
#   return, enter
#   escape, tab, space
#   backspace, delete, insert
#
# Lock Keys:
#   capslock, numlock, scrolllock
#
# Function Keys:
#   f1 - f12
#
# Miscellaneous:
#   menu, printscreen, pause
#
# Symbol Keys:
#   slash (/)
#   backslash (\\)
#   comma (,)
#   period (.)
#   dot (.)
#   semicolon (;)
#   apostrophe (')
#   quote (")
#   minus (-)
#   equal (=)
#   plus (+)
#   grave (`)
#   backtick (`)
#
# Bracket Keys:
#   leftbracket ([)
#   rightbracket (])
#   leftbrace ({)
#   rightbrace (})
#   leftparen (()
#   rightparen ())
#
# Keypad Keys:
#   kp_enter
#   kp_add
#   kp_subtract
#   kp_multiply
#   kp_divide
#   kp_decimal
#
# Single Character Keys:
#   a-z
#   A-Z
#   0-9
#   /
#   \\
#   [
#   ]
#   .
#   ,
#   ;
#   '
#   -
#   =
#
# Missing values automatically fall back to OmniGlyph defaults.

[shortcuts]

# General
quit = "ctrl+q"
focus_search = "slash"
history = "ctrl+h"
reload_collection = "ctrl+r"

# Navigation
next_category = "l"
prev_category = "h"

# Scrolling
scroll_down = "j"
scroll_up = "k"

# Sidebar
toggle_sidebar = "ctrl+b"
sidebar_next = "j"
sidebar_prev = "k"
sidebar_close = "return"

# Actions
copy_first = "return"

[behavior]

# Window behavior
esc_action = "hide"        # hide | quit
theme = "system"           # system | light | dark
close_on_copy = true
show_notifications = true

# Layout
window_width = 450
window_height = 500
sidebar_width = 180
grid_columns = 13

# Performance
batch_size = 30

# Scrolling
scroll_step = 120
"""

DEFAULT_DATA = {
    "shortcuts": {
        # General
        "quit": "ctrl+q",
        "focus_search": "slash",
        "history": "ctrl+h",
        "reload_collection": "ctrl+r",
        # Navigation
        "next_category": "l",
        "prev_category": "h",
        # Scrolling
        "scroll_down": "j",
        "scroll_up": "k",
        # Sidebar
        "toggle_sidebar": "ctrl+b",
        "close_sidebar": "escape",
        "sidebar_next": "j",
        "sidebar_prev": "k",
        "close_sidebar": "return",
        # Actions
        "copy_first": "return",
    },
    "behavior": {
        # Window behavior
        "esc_action": "hide",
        "theme": "system",
        "close_on_copy": True,
        "show_notifications": True,
        # Layout
        "window_width": 450,
        "window_height": 500,
        "sidebar_width": 180,
        "grid_columns": 13,
        # Performance
        "batch_size": 30,
        # Scrolling
        "scroll_step": 120,
    },
}

KEY_DISPLAY = {
    # Modifiers
    "ctrl": "Ctrl",
    "shift": "Shift",
    "alt": "Alt",
    "super": "Super",
    # Symbols
    "slash": "/",
    "backslash": "\\",
    "comma": ",",
    "period": ".",
    "dot": ".",
    "semicolon": ";",
    "apostrophe": "'",
    "quote": '"',
    "minus": "-",
    "equal": "=",
    "plus": "+",
    "grave": "`",
    "backtick": "`",
    # Brackets
    "leftbracket": "[",
    "rightbracket": "]",
    "leftbrace": "{",
    "rightbrace": "}",
    "leftparen": "(",
    "rightparen": ")",
    # Navigation
    "up": "↑",
    "down": "↓",
    "left": "←",
    "right": "→",
    "home": "Home",
    "end": "End",
    "pageup": "PgUp",
    "pagedown": "PgDn",
    # Editing
    "tab": "Tab",
    "space": "Space",
    "escape": "Esc",
    "return": "Enter",
    "enter": "Enter",
    "backspace": "Backspace",
    "delete": "Del",
    "insert": "Ins",
    # Lock keys
    "capslock": "Caps Lock",
    "numlock": "Num Lock",
    "scrolllock": "Scroll Lock",
    # Misc
    "menu": "Menu",
    "printscreen": "PrtSc",
    "pause": "Pause",
    # Keypad
    "kp_enter": "Num Enter",
    "kp_add": "Num +",
    "kp_subtract": "Num -",
    "kp_multiply": "Num *",
    "kp_divide": "Num /",
    "kp_decimal": "Num .",
}


class Config:
    def __init__(self):
        config_dir = Path(GLib.get_user_config_dir()) / "omniglyph"
        config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = config_dir / "config.toml"

        if not self.config_file.exists():
            self.config_file.write_text(
                DEFAULT_CONFIG,
                encoding="utf-8",
            )

        self.data = self._load_with_defaults()

    def _merge(self, base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge(base[key], value)
            else:
                base[key] = value

        return base

    def _load_with_defaults(self):
        try:
            with self.config_file.open("rb") as f:
                user_data = tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError):
            return deepcopy(DEFAULT_DATA)

        return self._merge(
            deepcopy(DEFAULT_DATA),
            user_data,
        )

    def load(self):
        self.data = self._load_with_defaults()
        return self.data

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

        parts = []

        for part in raw.split("+"):
            part_lower = part.lower()

            parts.append(
                KEY_DISPLAY.get(
                    part_lower,
                    part.upper() if len(part) == 1 else part.capitalize(),
                )
            )

        return "+".join(parts)
