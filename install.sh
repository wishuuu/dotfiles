#!/usr/bin/env bash
# Użycie: bash install.sh cli|desktop [ścieżka-do-nvim]
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
profile=${1:-cli}
case "$profile" in
  cli) names=(fish) ;;
  desktop) names=(fish ghostty hypr waybar fuzzel mako) ;;
  *) echo 'Profil musi być cli lub desktop' >&2; exit 1 ;;
esac
[[ $EUID -ne 0 ]] || { echo 'Uruchom jako zwykły użytkownik, bez sudo.' >&2; exit 1; }
config=${XDG_CONFIG_HOME:-$HOME/.config}
mkdir -p "$config"
sources=(); targets=()
for name in "${names[@]}"; do
  sources+=("$root/config/$name"); targets+=("$config/$name")
done
if [[ -n ${2:-} ]]; then
  nvim=$(cd -- "$2" && pwd)
  [[ -f $nvim/init.lua ]] || { echo 'Brak init.lua w repo Neovima' >&2; exit 1; }
  sources+=("$nvim"); targets+=("$config/nvim")
fi
# Najpierw sprawdź wszystkie kolizje; nie nadpisuj ani nie usuwaj plików.
for i in "${!targets[@]}"; do
  target=${targets[$i]}; source=${sources[$i]}
  if [[ -e $target || -L $target ]]; then
    if [[ ! -L $target ]] || [[ $(readlink "$target") != "$source" ]]; then
      echo "Kolizja: $target — przenieś istniejącą konfigurację do kopii zapasowej." >&2
      exit 1
    fi
  fi
done
for i in "${!targets[@]}"; do
  [[ -L ${targets[$i]} ]] || ln -s -- "${sources[$i]}" "${targets[$i]}"
  echo "${targets[$i]} -> ${sources[$i]}"
done
