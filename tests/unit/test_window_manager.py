from utils.window_manager import is_tiling_window_manager


def test_hyprland_signature_detected(monkeypatch):
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc123")
    monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
    assert is_tiling_window_manager() is True


def test_sway_socket_detected(monkeypatch):
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.setenv("SWAYSOCK", "/run/sway.sock")
    assert is_tiling_window_manager() is True


def test_xdg_current_desktop_match(monkeypatch):
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.delenv("SWAYSOCK", raising=False)
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME:i3")
    assert is_tiling_window_manager() is True


def test_gnome_alone_is_not_tiling(monkeypatch):
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.delenv("SWAYSOCK", raising=False)
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
    assert is_tiling_window_manager() is False


def test_no_env_vars_is_not_tiling(monkeypatch):
    monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
    monkeypatch.delenv("SWAYSOCK", raising=False)
    monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
    assert is_tiling_window_manager() is False
