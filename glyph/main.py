import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class AppWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Glyph")
        self.set_default_size(400, 200)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)

        title = Gtk.Label(label="Welcome to Glyph")


        button = Gtk.Button(label="press")
        button.connect("clicked", self.on_start_clicked)

        box.append(title)
        box.append(button)

        self.set_content(box)

    def on_start_clicked(self, button):
        print("hello!!!!")


class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.anishroy.glyph"
        )

    def do_activate(self):
        window = AppWindow(self)
        window.present()


app = MyApp()
app.run()
