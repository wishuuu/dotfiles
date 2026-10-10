#!/usr/bin/env bash
# Użycie: bash install.sh cli|desktop [ścieżka-do-nvim]
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
profile=${1:-cli}
case "$profile" in
  cli) names=(fish zellij) ;;
  desktop) names=(fish zellij ghostty hypr waybar fuzzel mako nord-panel) ;;
  *) echo 'Profil musi być cli lub desktop' >&2; exit 1 ;;
esac
[[ $EUID -ne 0 ]] || { echo 'Uruchom jako zwykły użytkownik, bez sudo.' >&2; exit 1; }
config=${XDG_CONFIG_HOME:-$HOME/.config}
mkdir -p "$config"
sources=(); targets=()
for name in "${names[@]}"; do
  sources+=("$root/config/$name"); targets+=("$config/$name")
done
# Każdy skrypt osobno — istniejące ~/.local/bin pozostaje nienaruszone.
for script in "$root"/bin/*; do
  [[ -f $script && -x $script ]] || continue
  sources+=("$script"); targets+=("$HOME/.local/bin/$(basename -- "$script")")
done
# Nie dowiązuj całego katalogu gh: hosts.yml może zawierać token OAuth.
sources+=("$root/config/gh/config.yml"); targets+=("$config/gh/config.yml")
if [[ -n ${2:-} ]]; then
  nvim=$(cd -- "$2" && pwd)
  [[ -f $nvim/init.lua ]] || { echo 'Brak init.lua w repo Neovima' >&2; exit 1; }
  sources+=("$nvim"); targets+=("$config/nvim")
fi
# Domyślnie odmów kolizji. setup ustawia katalog na automatyczne kopie.
conflicts=()
for i in "${!targets[@]}"; do
  target=${targets[$i]}; source=${sources[$i]}
  if [[ -e $target || -L $target ]]; then
    if [[ ! -L $target ]] || [[ $(readlink "$target") != "$source" ]]; then
      if [[ -z ${DOTFILES_BACKUP_DIR:-} ]]; then
        echo "Kolizja: $target — przenieś istniejącą konfigurację do kopii zapasowej." >&2
        exit 1
      fi
      conflicts+=("$target")
    fi
  fi
done
if [[ ${#conflicts[@]} -gt 0 ]]; then
  # Nie mieszaj dwóch wdrożeń ani nie nadpisuj wcześniejszej kopii.
  [[ ! -e $DOTFILES_BACKUP_DIR && ! -L $DOTFILES_BACKUP_DIR ]] || {
    echo "Katalog kopii już istnieje: $DOTFILES_BACKUP_DIR" >&2; exit 1;
  }
  mkdir -p -- "$DOTFILES_BACKUP_DIR"
  for target in "${conflicts[@]}"; do
    backup="$DOTFILES_BACKUP_DIR/${target#/}"
    mkdir -p -- "$(dirname -- "$backup")"
    mv -- "$target" "$backup"
    echo "Kopia: $target -> $backup"
  done
fi
for i in "${!targets[@]}"; do
  mkdir -p -- "$(dirname -- "${targets[$i]}")"
  [[ -L ${targets[$i]} ]] || ln -s -- "${sources[$i]}" "${targets[$i]}"
  echo "${targets[$i]} -> ${sources[$i]}"
done
