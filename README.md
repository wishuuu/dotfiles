# Dotfiles

Zwykłe pliki w `config/`, niezależne od Home Managera i NixOS.

```sh
git clone https://github.com/wishuuu/dotfiles ~/dotfiles
bash ~/dotfiles/install.sh desktop ~/nvim-cfg
# Bez GUI, np. WSL:
bash ~/dotfiles/install.sh cli ~/nvim-cfg
```

Drugi argument jest opcjonalny. Instalator tworzy dowiązania, odmawia nadpisania
istniejących plików i nie wymaga sudo. Repozytoriów nie przenoś po instalacji.
Przed instalacją ręcznie przenieś istniejące konfiguracje do kopii zapasowej.

## Pulpit Nord

Hyprland **0.55+ z Lua**: `config/hypr/hyprland.lua`, skróty: `bindings.lua`.
Stary `hyprland.conf` jest tylko przejściowym zabezpieczeniem dla sesji sprzed
migracji — nowa sesja wybiera `hyprland.lua`. Zmiana parsera wymaga ponownego
logowania, nie wystarczy `hyprctl reload`.

Motyw Nord/Frost, odstępy 3/6 px, zaokrąglenia 6 px, krótkie animacje.
Autorska tapeta Fjord (SVG + gotowy PNG) jest w `config/hypr/wallpapers/`;
wyświetla ją swaybg. GTK używa Nordic, ikony Papirus-Dark.
Aplikacje z własnymi motywami (np. Zen/Discord) mogą wymagać ustawienia ciemnego
wyglądu w ich preferencjach; motyw GTK nie zmienia wszystkich aplikacji.

| Skrót | Działanie |
| --- | --- |
| Win+Enter / C / D | Ghostty / zamknięcie okna / wybierak Fuzzel |
| Win+1…9 | Przejdź na pulpit |
| Win+Shift+1…9 | Przenieś okno i przejdź za nim |
| Win+Alt+1…9 | Wyślij okno, pozostań na obecnym pulpicie |
| Win+strzałki | Zmień fokus |
| Win+Ctrl+strzałki | Przesuń okno |
| Win+lewy/prawy przycisk myszy | Przesuwanie / zmiana rozmiaru |
| Win+F / V / J | Pełny ekran / okno pływające / kierunek podziału |
| Win+E / L | Pliki / blokada ekranu |
| Win+Space | Panel sterowania |
| Win+Shift+E / przycisk zasilania | Menu sesji i zasilania |
| Print / Win+Print | Zrzut obszaru / całego ekranu do schowka |

Ctrl+C/D pozostają dostępne dla aplikacji. Gest trzema palcami zmienia pulpit.
Waybar: panel po lewej, dziewięć pulpitów, zegar z kalendarzem, multimedia,
czuwanie, dźwięk, jasność, sieć, Bluetooth, bateria, tray i menu zasilania.
Klik na głośność otwiera mikser, prawy wycisza, rolka zmienia głośność.
Ikona czuwania wstrzymuje automatyczną blokadę. Domyślnie blokada po 10 minutach,
wygaszenie po 11; uśpienie blokuje ekran przez hypridle.

Panel (`config/nord-panel/`) ma aplikacje, katalogi, suwaki głośności/jasności,
multimedia, sieć, Bluetooth, tryb bez powiadomień i informacje o zasobach.
Nie tworzy nieistniejących katalogów. Wyłączenie, restart i wylogowanie wymagają
potwierdzenia; Esc zamyka panel. Nie działa stale w tle. Aplikacje i ścieżki
zmieniaj w `panel.py`, wygląd w `style.css`.

### Aktywacja w tym repo NixOS

Z katalogu głównego `nixos/`:

```sh
bash external/dotfiles/install.sh desktop
sudo nixos-rebuild switch --flake .#loki
```

Następnie zapisz pracę i **uruchom komputer ponownie** (lub zakończ sesję i zaloguj
się od nowa). Przebudowa instaluje `nord-panel`, swaybg i motywy oraz ustawia
`services.logind.settings.Login.HandlePowerKey = "ignore"`.
**Dopiero po aktywacji systemu krótkie naciśnięcie zasilania nie wyłącza laptopa.**
Na zablokowanym ekranie przycisk nie otwiera panelu. Długie przytrzymanie może
nadal sprzętowo odciąć zasilanie — konfiguracja pulpitu tego nie przechwytuje.

Kolejne zmiany dotfiles nie wymagają przebudowy: `hyprctl reload`, restart Waybara,
`makoctl reload`; panel odczytuje pliki przy ponownym otwarciu.
Fish: otwórz nowy terminal. Ghostty: `Ctrl+Shift+,` przeładowuje konfigurację.

Na innych dystrybucjach zainstaluj odpowiadające programy. Panel wymaga Python 3,
PyGObject i GTK3 oraz wrappera `nord-panel` uruchamiającego
`python3 ~/.config/nord-panel/panel.py "$@"`. Zależności akcji: wpctl, brightnessctl,
playerctl, makoctl, nm-connection-editor, blueman-manager, thunar, xdg-user-dir.
Obsługę przycisku zasilania ustaw również w logind. Ścieżka agenta Polkit
w `hyprland.lua` jest specyficzna dla NixOS — dostosuj ją do dystrybucji.
Przycisk Zen używa `zen-beta` (nazwa programu z obecnego flake).
Ghostty uruchamia `zellij attach --create main`, a Zellij używa Fish.
Na innych dystrybucjach zainstaluj oba programy i zadbaj o ich dostępność w PATH.

Zellij (`config/zellij/config.kdl`) startuje w trybie zablokowanych skrótów.
`Ctrl+a` otwiera tryb Tab: `1…9` i strzałki wybierają tab, `n` tworzy nowy,
a kolejne `Ctrl+a` wraca do ostatnio aktywnego taba. Motyw: Nord.
Dodatkowo po prefiksie: `c` tworzy tab, `p` przechodzi do poprzedniego,
`%` / `"` dzielą panel na prawo / w dół, `d` odłącza sesję. Te akcje ponownie blokują
skróty; `Esc` anuluje prefix i też blokuje. `r` zmienia nazwę taba, Enter
zatwierdza i blokuje, Esc cofa zmianę i blokuje.
Przejścia do pozostałych trybów pozostają domyślne, np. `Ctrl+p` -> Pane.
Ich bindy pozostają bez zmian; `Ctrl+g` pozwala wrócić do Locked.
Ghostty automatycznie tworzy/przywraca wspólną sesję `main`; do projektów użyj `sese`.
Zellij nie odtwarza sesji po restarcie systemu (wyłączona serializacja).

GitHub CLI: dowiązujemy tylko `config/gh/config.yml`, nigdy cały katalog `gh`.
Zaloguj się przez `gh auth login --web`, potem `gh auth setup-git`.
Tokeny w magazynie sekretów lub `~/.config/gh/hosts.yml` muszą pozostać lokalne.
Alias `gh co NUMER` otwiera pull request do pracy, edytor to Neovim.
Na innych dystrybucjach oba profile wymagają również Fish, Zellij i gh.

## Własne skrypty

Pliki wykonywalne w `bin/` są dowiązywane przez instalator do `~/.local/bin`.
Dodaj skrypt z `#!/usr/bin/env bash`, nadaj `chmod +x bin/nazwa` i ponownie
uruchom instalator. Na dystrybucjach innych niż NixOS sam dodaj `~/.local/bin`
do PATH. W Fish możesz użyć `fish_add_path ~/.local/bin`.

`sese` wybiera przez fzf bezpośrednie podkatalogi `~`, `~/personal`, `~/work`
(także ukryte i dowiązania), po czym tworzy sesję Zellij lub dołącza do istniejącej.
Wewnątrz Zellij przełącza sesję. Nazwa sesji zawiera nazwę katalogu i skrót
kanonicznej ścieżki. Wymaga Bash, GNU coreutils/findutils, fzf i Zellij.

Fish włącza integrację fzf, jeśli jest zainstalowane (`Ctrl+r`, `Ctrl+t`, `Alt+c`).

Repo nie zawiera haseł, tokenów, kluczy ani konfiguracji Neovima.
