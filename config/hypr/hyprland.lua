-- Hyprland >= 0.55 (Lua). Kolory: Nord / Frost.
local home = os.getenv("HOME")
local config = os.getenv("XDG_CONFIG_HOME") or (home .. "/.config")
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })
hl.env("XCURSOR_THEME", "Adwaita")
hl.env("XCURSOR_SIZE", "24")
hl.env("GTK_THEME", "Nordic")
hl.config({
    -- Jeden klasyczny motyw XCursor w kompozytorze i aplikacjach.
    cursor = { enable_hyprcursor = false },
    input = { kb_layout = "pl", follow_mouse = 1,
        touchpad = { natural_scroll = true, tap_to_click = true } },
    general = { gaps_in = 3, gaps_out = 6, border_size = 2,
        resize_on_border = true, layout = "dwindle",
        col = { active_border = "rgb(88c0d0)", inactive_border = "rgb(434c5e)" } },
    decoration = { rounding = 6,
        shadow = { enabled = true, range = 12, render_power = 3, color = "rgba(18202bcc)" },
        blur = { enabled = false } },
    animations = { enabled = true },
    dwindle = { preserve_split = true },
    misc = { disable_hyprland_logo = true, force_default_wallpaper = 0,
        background_color = "rgb(2e3440)" },
})
hl.curve("nord", { type = "bezier", points = { {0.2, 0.8}, {0.2, 1} } })
hl.animation({ leaf = "global", enabled = true, speed = 3, bezier = "nord" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2, bezier = "nord", style = "fade" })
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
hl.on("hyprland.start", function()
    for _, command in ipairs({
        "dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP HYPRLAND_INSTANCE_SIGNATURE",
        "waybar", "mako", "hypridle", "nm-applet --indicator",
        "nord-polkit-agent",
        "swaybg -i '" .. config .. "/hypr/wallpapers/nord.png' -m fill",
        "gsettings set org.gnome.desktop.interface gtk-theme Nordic",
        "gsettings set org.gnome.desktop.interface icon-theme Papirus-Dark",
        "gsettings set org.gnome.desktop.interface cursor-theme Adwaita",
        "gsettings set org.gnome.desktop.interface cursor-size 24",
        "hyprctl setcursor Adwaita 24",
        "gsettings set org.gnome.desktop.interface color-scheme prefer-dark",
    }) do hl.exec_cmd(command) end
end)
hl.window_rule({ name = "ignore-maximize", match = { class = ".*" }, suppress_event = "maximize" })
hl.window_rule({ name = "nord-panel", match = { class = "pl.oskar.NordPanel" },
    float = true, center = true, size = "680 680" })
dofile(config .. "/hypr/bindings.lua")
