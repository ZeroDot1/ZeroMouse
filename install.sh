#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v makepkg >/dev/null; then
  echo 'makepkg fehlt. Dieses Installationsskript benötigt Arch Linux oder eine Arch-basierte Distribution.' >&2
  exit 1
fi
makepkg -f
package_file="$(makepkg --packagelist | tail -n 1)"
sudo pacman -U --needed "$package_file"
echo 'Installiert. Thema im Desktop unter „ZeroMouse“ auswählen.'
