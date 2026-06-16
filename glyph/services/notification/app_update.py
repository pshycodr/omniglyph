import json
import threading
import urllib.request
import webbrowser

from gi.repository import Gio, GLib

from constants import APP_ID, VERSION

GITHUB_API = "https://api.github.com/repos/pshycodr/omniglyph/releases/latest"

LATEST_RELEASE_URL = "https://github.com/pshycodr/omniglyph/releases/latest"


def _parse_version(version: str) -> tuple:
    version = version.strip().lstrip("v")
    return tuple(int(part) for part in version.split("."))


def _show_update_notification(app, latest_version):
    try:
        notification = Gio.Notification.new(f"OmniGlyph {latest_version} Available")

        notification.set_body("A newer version of OmniGlyph is available.")

        notification.add_button(
            "Check What's New",
            "app.open-release",
        )

        app.send_notification(
            "omniglyph-update",
            notification,
        )

    except Exception:
        pass

    return False


def _check_for_updates(app):
    try:
        request = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": "OmniGlyph"},
        )

        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:
            data = json.loads(response.read().decode("utf-8"))

        latest_version = data["tag_name"]

        if _parse_version(latest_version) > _parse_version(VERSION):
            GLib.idle_add(
                _show_update_notification,
                app,
                latest_version.lstrip("v"),
            )

    except Exception:
        # Fail silently
        pass


def setup_update_notifications(app):
    try:
        action = Gio.SimpleAction.new(
            "open-release",
            None,
        )

        action.connect(
            "activate",
            lambda *_: webbrowser.open(LATEST_RELEASE_URL),
        )

        app.add_action(action)

    except Exception:
        pass


def check_for_updates_async(app):
    threading.Thread(
        target=_check_for_updates,
        args=(app,),
        daemon=True,
        name="OmniGlyphUpdateChecker",
    ).start()
