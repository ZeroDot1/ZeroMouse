#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for tool in makepkg pacman sudo; do
  if ! command -v "$tool" >/dev/null; then
    printf 'Required Arch Linux installation command is missing: %s\n' "$tool" >&2
    exit 1
  fi
done
if (( EUID == 0 )); then
  echo 'Run this script as a regular user. It requests sudo for pacman.' >&2
  exit 1
fi
makepkg -f
package_list="$(makepkg --packagelist)"
mapfile -t packages <<< "$package_list"
if (( ${#packages[@]} != 1 )) || [[ ! -f "${packages[0]}" ]]; then
  echo 'Expected exactly one built ZeroMouse package.' >&2
  exit 1
fi
sudo pacman -U --needed -- "${packages[0]}"
echo 'Installed. Select ZeroMouse in your desktop cursor settings.'
