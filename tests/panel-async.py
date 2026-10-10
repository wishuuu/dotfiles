"""Test odświeżania bez GTK/display: atrapy UI i kolejka głównego wątku."""
import importlib.util
from pathlib import Path
from queue import Queue
import sys
import threading
from types import ModuleType, SimpleNamespace

sys.dont_write_bytecode = True
main_thread = threading.get_ident()
callbacks = Queue()


class Application:
    def __init__(self, **kwargs):
        pass


class Widget:
    def __init__(self):
        self.value = None

    def set_text(self, value):
        assert threading.get_ident() == main_thread, "GTK poza wątkiem UI"
        self.value = value

    set_value = set_text
    set_sensitive = set_text
    set_tooltip_text = set_text

    def has_focus(self):
        return False


gi = ModuleType("gi")
gi.require_version = lambda *args: None
repository = ModuleType("gi.repository")
repository.Gtk = SimpleNamespace(Application=Application)
repository.Gio = SimpleNamespace(ApplicationFlags=SimpleNamespace(HANDLES_COMMAND_LINE=0))
repository.Gdk = SimpleNamespace()
repository.GLib = SimpleNamespace(idle_add=lambda *args: callbacks.put(args))
sys.modules["gi"] = gi
sys.modules["gi.repository"] = repository
source = Path(__file__).resolve().parents[1] / "config/nord-panel/panel.py"
spec = importlib.util.spec_from_file_location("nord_panel", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.Panel()
app.window = object()
for name in ("clock", "volume", "brightness", "track", "resources"):
    setattr(app, name, Widget())
started = threading.Event()
release = threading.Event()
reads = []
values = ("Volume: 0.5", ("50", "100"), "Test track", "Test resources")


def slow_read():
    assert threading.get_ident() != main_thread
    reads.append(True)
    started.set()
    assert release.wait(5)
    return values


def deliver():
    callback, *args = callbacks.get(timeout=5)
    assert callback(*args) is False


module.read_status = slow_read
assert app.refresh() is True  # Wraca mimo nadal zablokowanego odczytu.
assert started.wait(5)
assert not release.is_set()
assert app.refresh() is True
assert len(reads) == 1, "Nałożone odczyty"
release.set()
deliver()
assert app.polling is None
assert app.track.value == "Test track"
assert app.resources.value == "Test resources"
assert not app.refreshing

# Wynik dla poprzedniego okna nie zmienia nowego okna.
started.clear()
release.clear()
app.refresh()
assert started.wait(5)
app.window = object()
app.track.value = "new window"
release.set()
deliver()
assert app.track.value == "new window"
assert app.polling is None

# Awaria odczytu odblokowuje kolejne próby; niedostępne suwaki są wyłączone.
def failed_read():
    raise OSError("test failure")


module.read_status = failed_read
app.refresh()
deliver()
assert app.polling is None
assert app.volume.value is False
assert app.brightness.value is False
app.window = None
assert app.refresh() is False
print("PASS: responsywność, brak nakładania odczytów, wątek UI, stare okno, awaria")
