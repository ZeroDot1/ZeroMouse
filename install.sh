#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v makepkg >/dev/null; then
  echo 'makepkg is missing. This installer requires Arch Linux or an Arch-based distribution.' >&2
  exit 1
fi
makepkg -f
package_file="$(makepkg --packagelist | tail -n 1)"
sudo pacman -U --needed "$package_file"
echo 'Installed. Select ZeroMouse in your desktop cursor settings.'
