"""Uruchom z Pythonem PyGObject i GTK3, w izolowanym Xvfb + dbus-run-session.
Nie wykonuje operacji systemowych; screenshot opcjonalnie w NORD_TEST_SCREENSHOT.
"""
import importlib.util
import os
from pathlib import Path
import sys

source = Path(__file__).resolve().parents[1] / "config/nord-panel/panel.py"
spec = importlib.util.spec_from_file_location("nord_panel", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Gtk, GLib, Gdk = module.Gtk, module.GLib, module.Gdk
app = module.Panel()
errors = []


def check():
    try:
        assert app.window is not None
        assert app.stack.get_visible_child_name() == "home"
        css = Gtk.CssProvider()
        css.load_from_path(str(source.parents[1] / "waybar/style.css"))
        calls = []
        app.launch = lambda args, close=False: calls.append(args)
        # Domyślna odpowiedź na potwierdzeniu musi być bezpieczna.
        def cancel():
            for window in Gtk.Window.list_toplevels():
                if isinstance(window, Gtk.MessageDialog):
                    window.response(Gtk.ResponseType.CANCEL)
            return False
        GLib.timeout_add(100, cancel)
        app.power("Test", ["systemctl", "poweroff"], True)
        assert not calls, "Anulowanie wykonało akcję!"
        def accept():
            for window in Gtk.Window.list_toplevels():
                if isinstance(window, Gtk.MessageDialog):
                    window.response(Gtk.ResponseType.OK)
            return False
        GLib.timeout_add(100, accept)
        app.power("Test", ["TEST-NO-EXEC"], True)
        assert calls == [["TEST-NO-EXEC"]]
        app.stack.set_visible_child_name("power")
        assert app.stack.get_visible_child_name() == "power"
        app.stack.set_visible_child_name("home")
    except Exception as error:
        errors.append(error)
    GLib.timeout_add(500, finish)
    return False


def finish():
    screenshot = os.getenv("NORD_TEST_SCREENSHOT")
    if screenshot and app.window:
        window = app.window.get_window()
        pixbuf = Gdk.pixbuf_get_from_window(window, 0, 0, window.get_width(), window.get_height())
        pixbuf.savev(screenshot, "png", [], [])
    app.window.close()
    return False


GLib.timeout_add(1500, check)
app.run([sys.argv[0]])
if errors:
    raise errors[0]
print("PASS: panel GTK, zakładki, anulowanie/potwierdzenie, zamknięcie")
