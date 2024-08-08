import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        # Create a Builder
        builder = Gtk.Builder()
        builder.add_from_file("./ui/main.ui")

        # Obtain and show the main window
        self.win = builder.get_object("main")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.win.present()
        
        
app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)