import sys
from pathlib import Path

import pytest

GLYPH_DIR = Path(__file__).parent.parent / "glyph"
sys.path.insert(0, str(GLYPH_DIR))

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


@pytest.fixture(scope="session", autouse=True)
def gtk_app():
    """
    Session-scoped GTK init. Widget tests depend on this implicitly
    via autouse. Unit tests that only need Gdk constants (shortcuts,
    keyvals) work fine without a real Application, but Gtk.init must
    still run once before any widget is constructed.
    """
    from gi.repository import Adw, Gtk

    Gtk.init()
    app = Adw.Application(application_id="dev.anishroy.omniglyph.test")
    yield app


@pytest.fixture
def tmp_config_dir(tmp_path, monkeypatch):
    """Redirect GLib's user config dir to an isolated tmp_path."""
    monkeypatch.setattr("gi.repository.GLib.get_user_config_dir", lambda: str(tmp_path))
    return tmp_path


@pytest.fixture
def tmp_history_dir(tmp_path, monkeypatch):
    """Redirect history service storage to an isolated tmp_path."""
    import services.history as history_mod

    monkeypatch.setattr(history_mod, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(history_mod, "_HISTORY_FILE", tmp_path / "history.json")
    return tmp_path
