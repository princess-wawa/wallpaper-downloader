import sys
import gi
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw, GdkPixbuf, GLib
from buttons import buttons
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
        self.refresh.connect("clicked", self.on_refresh_action)
        
        self.win.present()
        
        
        

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
        if hasattr(self.win, "info"):
            info = self.win.info["images"][0]
            about = Adw.AboutWindow(transient_for=self.props.active_window,
                                    artists=[info['artist']],
                                    website="https://nekos.moe/post/" + info['id'])
            about.present()
    
    def on_settings_action(self,widget):
        return
    
    def on_download_action(self, widget):
        buttons.download()
        
    def on_wallpaper_action(self,widget):
        buttons.wallpaper()

    def on_refresh_action(self,widget):
        jp.reloadimage()
        
    
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
