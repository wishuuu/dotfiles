#!/usr/bin/env python3
"""Nord: niewielkie centrum pulpitu. GTK3, bez usług działających w tle."""
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk

HOME = Path.home()


def output(*args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL, timeout=1).strip()
    except (OSError, subprocess.SubprocessError):
        return ""


class Panel(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="pl.oskar.NordPanel", flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.window = None
        self.refreshing = False
        self.pending = {}

    def do_command_line(self, command_line):
        self.activate()
        self.stack.set_visible_child_name("power" if "--power" in command_line.get_arguments() else "home")
        return 0

    def do_activate(self):
        if self.window is not None:
            self.window.present()
            return
        css = Gtk.CssProvider()
        css.load_from_path(str(Path(__file__).with_name("style.css")))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window = Gtk.ApplicationWindow(application=self, title="Nord • centrum sterowania")
        self.window.set_default_size(680, 680)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_resizable(True)
        self.window.connect("key-press-event", self.keypress)
        self.window.connect("destroy", self.destroyed)
        header = Gtk.HeaderBar(title="NORD", subtitle="Twoja przestrzeń")
        header.set_show_close_button(True)
        header.set_decoration_layout(":close")
        self.window.set_titlebar(header)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.window.add(scroll)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_border_width(18)
        scroll.add(root)
        self.clock = self.label("", "clock")
        root.pack_start(self.clock, False, False, 0)
        nav = Gtk.Box(spacing=6, homogeneous=True)
        root.pack_start(nav, False, False, 0)
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE, transition_duration=120)
        for name, text in [("home", "󰕮  Pulpit"), ("power", "󰐥  Sesja i zasilanie")]:
            nav.pack_start(self.button(text, lambda _, n=name: self.stack.set_visible_child_name(n)), True, True, 0)
        root.pack_start(self.stack, True, True, 0)
        self.status = self.label("", "status")
        self.status.set_line_wrap(True)
        root.pack_end(self.status, False, False, 0)
        self.build_home()
        self.build_power()
        self.window.show_all()
        self.refresh()
        self.timer = GLib.timeout_add_seconds(3, self.refresh)
        self.window.present()

    def destroyed(self, _):
        GLib.source_remove(self.timer)
        for source in self.pending.values():
            GLib.source_remove(source)
        self.pending.clear()
        self.window = None

    def keypress(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.window.close()
            return True
        return False

    @staticmethod
    def label(text, style):
        label = Gtk.Label(label=text, xalign=0)
        label.get_style_context().add_class(style)
        return label

    @staticmethod
    def button(text, callback, style=None):
        button = Gtk.Button(label=text)
        button.connect("clicked", callback)
        if style:
            button.get_style_context().add_class(style)
        return button

    def launch(self, args, close=False):
        try:
            # Asynchronicznie; żadnych poleceń przez shell ani interpolacji ścieżek.
            process = Gio.Subprocess.new(args, Gio.SubprocessFlags.STDOUT_SILENCE | Gio.SubprocessFlags.STDERR_PIPE)
            def done(proc, result):
                try:
                    _, _, error = proc.communicate_utf8_finish(result)
                    if not proc.get_successful() and self.window:
                        self.status.set_text((error or "Nie udało się wykonać polecenia.").strip()[:240])
                except GLib.Error as error:
                    if self.window:
                        self.status.set_text(str(error))
            process.communicate_utf8_async(None, None, done)
            if close:
                self.window.close()
        except GLib.Error as error:
            self.status.set_text(str(error))

    def section(self, box, text):
        box.pack_start(self.label(text, "section"), False, False, 0)

    def grid(self, box, entries, columns=3):
        grid = Gtk.Grid(column_spacing=6, row_spacing=6, column_homogeneous=True)
        for i, (text, callback) in enumerate(entries):
            grid.attach(self.button(text, callback), i % columns, i // columns, 1, 1)
        box.pack_start(grid, False, False, 0)

    def open_path(self, path):
        if not path.is_dir():
            self.status.set_text(f"Katalog nie istnieje: {path}")
            return
        self.launch(["thunar", str(path)], close=True)

    def build_home(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.stack.add_named(box, "home")
        self.section(box, "APLIKACJE")
        apps = [("  Terminal", ["ghostty"]), ("󰖟  Zen", ["zen-beta"]),
                ("󰙯  Discord", ["discord"]), ("󰓇  Spotify", ["spotify"]),
                ("󰈙  Dokumenty", ["libreoffice"]), ("󰍉  Wszystkie", ["fuzzel"])]
        self.grid(box, [(name, lambda _, a=args: self.launch(a, close=True)) for name, args in apps])
        self.section(box, "MIEJSCA")
        downloads = Path(output("xdg-user-dir", "DOWNLOAD") or str(HOME / "Downloads"))
        paths = [("󰋜  Dom", HOME), ("󰇚  Pobrane", downloads),
                 ("󰲋  Work", HOME / "work"), ("󰉋  Personal", HOME / "personal")]
        self.grid(box, [(name, lambda _, p=path: self.open_path(p)) for name, path in paths], 4)
        self.section(box, "DŹWIĘK I EKRAN")
        self.volume = self.slider(box, "󰕾  Głośność", "volume")
        self.brightness = self.slider(box, "󰃠  Jasność", "brightness")
        self.grid(box, [
            ("󰝟  Wycisz", lambda _: self.launch(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])),
            ("󰍬  Mikrofon", lambda _: self.launch(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])),
            ("󰒓  Mikser", lambda _: self.launch(["pavucontrol"])),
        ])
        self.section(box, "TERAZ ODTWARZANE")
        self.track = self.label("Brak odtwarzania", "track")
        self.track.set_ellipsize(3)
        box.pack_start(self.track, False, False, 0)
        self.grid(box, [(text, lambda _, a=action: self.launch(["playerctl", a])) for text, action in
                        [("󰒮  Poprzedni", "previous"), ("󰐎  Graj / pauza", "play-pause"), ("󰒭  Następny", "next")]])
        self.section(box, "ŁĄCZNOŚĆ I SYSTEM")
        self.grid(box, [
            ("󰤨  Sieć", lambda _: self.launch(["nm-connection-editor"])),
            ("󰂯  Bluetooth", lambda _: self.launch(["blueman-manager"])),
            ("󰌶  Powiadomienia", lambda _: self.launch(["makoctl", "mode", "-t", "do-not-disturb"])),
        ])
        self.resources = self.label("", "status")
        box.pack_start(self.resources, False, False, 0)

    def slider(self, box, text, kind):
        row = Gtk.Box(spacing=10)
        label = self.label(text, "control-label")
        label.set_size_request(135, -1)
        row.pack_start(label, False, False, 0)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0 if kind == "volume" else 1, 100, 1)
        scale.set_digits(0)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.set_hexpand(True)
        scale.connect("value-changed", self.slider_changed, kind)
        row.pack_start(scale, True, True, 0)
        box.pack_start(row, False, False, 0)
        return scale

    def slider_changed(self, scale, kind):
        if self.refreshing:
            return
        if kind in self.pending:
            GLib.source_remove(self.pending[kind])
        value = round(scale.get_value())
        def apply():
            self.pending.pop(kind, None)
            self.launch(["wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SINK@", f"{value}%"] if kind == "volume"
                     else ["brightnessctl", "set", f"{value}%"])
            return False
        self.pending[kind] = GLib.timeout_add(120, apply)

    def build_power(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.stack.add_named(box, "power")
        self.section(box, "SPOKOJNY KONIEC DNIA")
        hint = self.label("Wyłączenie, restart i wylogowanie wymagają potwierdzenia.\nPrzed wyjściem zapisz swoją pracę.", "status")
        hint.set_line_wrap(True)
        box.pack_start(hint, False, False, 8)
        for text, args, confirm in [
            ("󰌾  Zablokuj ekran", ["loginctl", "lock-session"], False),
            ("󰤄  Uśpij laptop", ["systemctl", "suspend"], False),
            ("󰍃  Wyloguj", ["hyprctl", "dispatch", "hl.dsp.exit()"], True),
            ("󰜉  Uruchom ponownie", ["systemctl", "reboot"], True),
            ("󰐥  Wyłącz laptop", ["systemctl", "poweroff"], True),
        ]:
            box.pack_start(self.button(text, lambda _, a=args, t=text, c=confirm: self.power(t, a, c), "power"), False, False, 0)

    def power(self, title, args, confirm):
        if confirm:
            dialog = Gtk.MessageDialog(transient_for=self.window, modal=True,
                                       message_type=Gtk.MessageType.QUESTION, text=title.strip())
            dialog.format_secondary_text("Niezapisane zmiany mogą zostać utracone. Kontynuować?")
            dialog.add_button("Anuluj", Gtk.ResponseType.CANCEL)
            dialog.add_button("Potwierdź", Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.CANCEL)
            response = dialog.run()
            dialog.destroy()
            if response != Gtk.ResponseType.OK:
                return
        self.launch(args)

    def refresh(self):
        self.clock.set_text(datetime.datetime.now().strftime("%H:%M   /   %d.%m.%Y"))
        self.refreshing = True
        volume = output("wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@")
        try:
            if "volume" not in self.pending and not self.volume.has_focus():
                self.volume.set_value(float(volume.split()[1]) * 100)
            self.volume.set_sensitive(True)
            self.volume.set_tooltip_text("Wyciszono" if "MUTED" in volume else "Głośność wyjścia")
        except (ValueError, IndexError):
            self.volume.set_sensitive(False)
        try:
            value = int(output("brightnessctl", "get")) / int(output("brightnessctl", "max")) * 100
            if "brightness" not in self.pending and not self.brightness.has_focus():
                self.brightness.set_value(value)
            self.brightness.set_sensitive(True)
        except (ValueError, ZeroDivisionError):
            self.brightness.set_sensitive(False)
        self.refreshing = False
        track = output("playerctl", "metadata", "--format", "{{artist}} — {{title}}")
        self.track.set_text(track or "Cisza • brak aktywnego odtwarzacza")
        self.track.set_tooltip_text(track)
        mem = {}
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                key, value = line.split(":", 1)
                mem[key] = int(value.split()[0])
            used = (mem["MemTotal"] - mem["MemAvailable"]) / 1048576
            free = shutil.disk_usage(HOME).free / (1024 ** 3)
            self.resources.set_text(f"RAM {used:.1f} / {mem['MemTotal'] / 1048576:.1f} GiB   •   Wolne {free:.0f} GiB   •   CPU load {os.getloadavg()[0]:.2f}")
        except (OSError, KeyError, ValueError):
            self.resources.set_text("")
        return True


if __name__ == "__main__":
    raise SystemExit(Panel().run(sys.argv))
