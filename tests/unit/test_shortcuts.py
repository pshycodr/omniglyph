from gi.repository import Gdk

from shortcuts import _parse_shortcut


def test_ctrl_modifier():
    keyval, mods = _parse_shortcut("ctrl+q")
    assert keyval == Gdk.KEY_q
    assert mods == Gdk.ModifierType.CONTROL_MASK


def test_multiple_modifiers():
    keyval, mods = _parse_shortcut("ctrl+shift+h")
    assert keyval == Gdk.KEY_h
    assert mods == (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK)


def test_named_key_slash():
    keyval, mods = _parse_shortcut("slash")
    assert keyval == Gdk.KEY_slash
    assert mods == Gdk.ModifierType(0)


def test_single_char_key():
    keyval, mods = _parse_shortcut("j")
    assert keyval == Gdk.unicode_to_keyval(ord("j"))
    assert mods == Gdk.ModifierType(0)


def test_empty_shortcut_returns_none():
    keyval, mods = _parse_shortcut("")
    assert keyval is None
    assert mods == Gdk.ModifierType(0)


def test_none_shortcut_returns_none():
    keyval, mods = _parse_shortcut(None)
    assert keyval is None


def test_unknown_key_name_returns_none():
    keyval, mods = _parse_shortcut("ctrl+nonexistentkey")
    assert keyval is None
