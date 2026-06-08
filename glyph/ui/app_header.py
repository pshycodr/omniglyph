import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk

VERSION = "v0.1.1"


class AppHeader(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()

        menu = Gio.Menu()

        menu.append("About", "app.about")
        menu.append("View on GitHub", "app.github")

        menu_button = Gtk.MenuButton(
            icon_name="open-menu-symbolic",
            menu_model=menu,
        )

        self.pack_end(menu_button)


def setup_actions(window):
    app = window.get_application()

    about_action = Gio.SimpleAction.new(
        "about",
        None,
    )

    about_action.connect(
        "activate",
        lambda action, param: show_about_dialog(window),
    )

    app.add_action(about_action)

    github_action = Gio.SimpleAction.new(
        "github",
        None,
    )

    github_action.connect(
        "activate",
        lambda action, param: open_github(),
    )

    app.add_action(github_action)


def open_github():
    Gio.AppInfo.launch_default_for_uri(
        "https://github.com/pshycodr/omniglyph",
        None,
    )


def show_about_dialog(window):
    about = Adw.AboutDialog(
        application_name="OmniGlyph",
        application_icon="dev.anishroy.omniglyph",
        version=VERSION,
        developer_name="pshycodr",
    )

    about.set_comments("A fast emoji and Unicode symbol picker for Linux.")

    about.set_website("https://github.com/pshycodr/omniglyph")

    about.set_issue_url("https://github.com/pshycodr/omniglyph/issues")

    about.set_license_type(Gtk.License.GPL_3_0)

    about.set_copyright("© 2026 pshycodr")

    about.add_credit_section(
        "Created by",
        ["Anish Roy (pshycodr)"],
    )

    about.add_credit_section(
        "Built with",
        [
            "Python",
            "GTK4",
            "Libadwaita",
        ],
    )

    about.add_credit_section(
        "Thanks to",
        [
            "GTK developers",
            "GNOME community",
            "Unicode Consortium",
            "Open source contributors",
        ],
    )

    about.present(window)
