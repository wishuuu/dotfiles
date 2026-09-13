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
Terminal domyślnie używa powłoki logowania użytkownika; ustaw Fish przez `chsh`.

Repo nie zawiera haseł, tokenów, kluczy ani konfiguracji Neovima.
