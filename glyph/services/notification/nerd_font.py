from gi.repository import Gio, PangoCairo

import webbrowser

NERD_FONT_URL = "https://www.nerdfonts.com/"


def has_nerd_font():
    try:
        fontmap = PangoCairo.FontMap.get_default()

        return any(
            "Nerd Font" in family.get_name() for family in fontmap.list_families()
        )

    except Exception:
        return False


def _show_nerd_font_notification(app):
    try:
        notification = Gio.Notification.new("Nerd Font Required")

        notification.set_body(
            "Install a Nerd Font to display icons from the Nerd Fonts collection."
        )

        notification.add_button(
            "Get Nerd Fonts",
            "app.open-nerd-fonts",
        )

        app.send_notification(
            "omniglyph-nerd-font",
            notification,
        )

    except Exception:
        pass

    return False


def setup_nerd_font_actions(app):
    try:
        action = Gio.SimpleAction.new(
            "open-nerd-fonts",
            None,
        )

        action.connect(
            "activate",
            lambda *_: webbrowser.open(NERD_FONT_URL),
        )

        app.add_action(action)

    except Exception:
        pass


def notify_if_nerd_font_missing(app):
    print("NERD FONT NOTIFICATION CHECK")
    print(type(app))
    # if has_nerd_font():
    #     return

    _show_nerd_font_notification(app)
