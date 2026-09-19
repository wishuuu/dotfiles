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

Skróty: `config/hypr/bindings.conf`; ustawienia pulpitu: `hyprland.conf`.
Hyprland przeładowuje konfigurację automatycznie (także `hyprctl reload`).
Waybar uruchom ponownie po zmianach, Mako: `makoctl reload`.
Fish: otwórz nowy terminal. Ghostty: `Ctrl+Shift+,` przeładowuje konfigurację.

Na innych dystrybucjach zainstaluj odpowiadające programy. Ścieżka do agenta
Polkit w `hyprland.conf` jest specyficzna dla NixOS — dostosuj ją do dystrybucji.
Ghostty uruchamia `zellij attach --create main`, a Zellij używa Fish.
Na innych dystrybucjach zainstaluj oba programy i zadbaj o ich dostępność w PATH.

Zellij (`config/zellij/config.kdl`) startuje w trybie zablokowanych skrótów.
`Ctrl+a` otwiera tryb Tab: `1…9` i strzałki wybierają tab, `n` tworzy nowy,
a kolejne `Ctrl+a` wraca do ostatnio aktywnego taba. Te akcje ponownie blokują
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
