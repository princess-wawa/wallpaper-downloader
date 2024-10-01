import sys
import gi
import threading
import json
from pathlib import Path
import time

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw, GdkPixbuf, GLib, Gdk
import buttons as buttons
import jsonparser as jp

apppath = str(Path(__file__).parent.parent / "ui" / "main.ui") 

class wallpaperdownloaderApplication(Adw.Application):
    """The main application singleton class."""
    
    __gtype_name__ = 'WallpaperDownloaderWindow'
    settings = Gtk.Template.Child("settings")
    download = Gtk.Template.Child("download")
    wallpaper = Gtk.Template.Child("wallpaper")
    
    def __init__(self):
        super().__init__(application_id='wawa.wallpaperdownloader',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.quit, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('show-art-about', self.on_art_about_action)
                
    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        # Create a Builder
        builder = Gtk.Builder()
        builder.add_from_file(apppath)

        # Obtain and show the main window
        self.win = builder.get_object("main")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.win.set_title("wallpaper Downloader")
        
        
        # set button up references
        self.settings = builder.get_object("settings")
        self.download = builder.get_object("download")
        self.wallpaper = builder.get_object("wallpaper")
        self.refresh = builder.get_object("refresh")
        self.settings.connect("clicked", self.on_settings_action)
        self.download.connect("clicked", self.on_download_action)
        self.wallpaper.connect("clicked", self.on_wallpaper_action)
        self.refresh.connect("clicked", self.async_on_refresh_action)
        
        #get things on the window
        self.query = builder.get_object("query")
        self.image = builder.get_object("image")
        self.spinner = builder.get_object("spinner")
        self.spinner.stop()
        self.spinner.set_visible(False)
        
        self.win.present()
        path = str(Path(__file__).parent.parent / "response" / "response.jpg")
        self.image.set_from_file(path)

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Wallpaper Downloader',
                                application_icon='/usr/share/icons/Adwaita/symbolic/emblems/emblem-photos-symbolic.svg',
                                developer_name='wawa',
                                version='0.0.1',
                                developers=['Princess_wawa'],
                                copyright='© 2024 princess_wawa')
        about.present()

    def on_art_about_action(self, widget, _):
        """Callback for the app.about action."""
        response = jp.getresponce()
        if response.get("Source", {}) != {}:
            about = Adw.AboutWindow(transient_for=self.props.active_window,
                                    artists=[response['Author']],
                                    website=response['Source'])
        else:
            about = Adw.AboutWindow(transient_for=self.props.active_window,
                                    artists=[response['Author']])
        about.present()

    def on_settings_action(self,widget):
        return
    
    def on_download_action(self, widget):
        buttons.download()
        
    def on_wallpaper_action(self,widget):
        buttons.wallpaper()
    
    def show_error_dialog(self, aaa, title, message):
        dialog = Adw.AlertDialog.new(title, None)
        dialog.set_body(message)
        dialog.add_response("ok", "_OK")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.connect("response", self.on_response)
        dialog.present(self.refresh)

    def on_response(self, dialog, response):
        return
    
    def async_on_refresh_action(self, widget=""):
        if jp.isqueryneeded():
            currentquery = ""
            currentquery = str(self.query.get_text())
            if currentquery == "":
                self.show_error_dialog(self, "no query provided", "please enter a query")
                return
            jp.setquery(currentquery)
        
        t = threading.Thread(target=self.on_refresh_action, args=(self,))
        t.start()
        self.image.set_visible(False)
        self.spinner.set_visible(True)
        self.spinner.start()
        t.join

        
    def on_refresh_action(self, widget=""):
        a = jp.reloadimage()
        if a != True:
            error = json.loads(a[1].decode('utf-8')).get("errors")[0]
            # ^ this is unreadable but it gets the error out of strings like b'{"errors":["Not found"]}'
            print(f"HTTP status code: {a[0]}, {a[1]}")
            self.show_error_dialog(self, f"HTTP status code:{a[0]}", f"{error}")
        path = str(Path(__file__).parent.parent / "response" / "response.jpg")
        self.image.set_from_file(path)
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.image.set_visible(True)
        
        
    
    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main():
    """The application's entry point."""
    app = wallpaperdownloaderApplication()
    app.run(sys.argv)
    
main()
