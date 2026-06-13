from gi.repository import Gdk

_NAMED_KEYS = {
    "slash": Gdk.KEY_slash,
    "escape": Gdk.KEY_Escape,
    "return": Gdk.KEY_Return,
    "enter": Gdk.KEY_Return,
    "right": Gdk.KEY_Right,
    "left": Gdk.KEY_Left,
    "up": Gdk.KEY_Up,
    "down": Gdk.KEY_Down,
    "tab": Gdk.KEY_Tab,
    "space": Gdk.KEY_space,
    "backspace": Gdk.KEY_BackSpace,
    "delete": Gdk.KEY_Delete,
    "home": Gdk.KEY_Home,
    "end": Gdk.KEY_End,
    "pageup": Gdk.KEY_Page_Up,
    "pagedown": Gdk.KEY_Page_Down,
    "f1": Gdk.KEY_F1,
    "f2": Gdk.KEY_F2,
    "f3": Gdk.KEY_F3,
    "f4": Gdk.KEY_F4,
    "f5": Gdk.KEY_F5,
    "f6": Gdk.KEY_F6,
    "f7": Gdk.KEY_F7,
    "f8": Gdk.KEY_F8,
    "f9": Gdk.KEY_F9,
    "f10": Gdk.KEY_F10,
    "f11": Gdk.KEY_F11,
    "f12": Gdk.KEY_F12,
}


def _parse_shortcut(shortcut):
    if not shortcut:
        return None, Gdk.ModifierType(0)

    parts = [p.strip().lower() for p in shortcut.split("+")]
    mods = Gdk.ModifierType(0)
    key_parts = []

    for p in parts:
        if p == "ctrl":
            mods |= Gdk.ModifierType.CONTROL_MASK
        elif p == "shift":
            mods |= Gdk.ModifierType.SHIFT_MASK
        elif p == "alt":
            mods |= Gdk.ModifierType.ALT_MASK
        elif p == "super":
            mods |= Gdk.ModifierType.SUPER_MASK
        else:
            key_parts.append(p)

    key_str = "+".join(key_parts)
    keyval = _NAMED_KEYS.get(key_str)
    if keyval is None and len(key_str) == 1:
        keyval = Gdk.unicode_to_keyval(ord(key_str))

    return keyval, mods
