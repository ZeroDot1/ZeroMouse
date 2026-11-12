#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="$(tr -d '\r\n' < "$root/VERSION")"
out_dir="${1:-$root/dist}"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

mkdir -p "$out_dir" "$stage/DEBIAN" \
  "$stage/usr/share/icons/ZeroMouse" \
  "$stage/usr/share/doc/zeromouse-cursor-theme/preview"
cp -a "$root/zeromouse/." "$stage/usr/share/icons/ZeroMouse/"
cp -a "$root/preview/." "$stage/usr/share/doc/zeromouse-cursor-theme/preview/"
install -m644 "$root/LICENSE" "$stage/usr/share/doc/zeromouse-cursor-theme/copyright"
install -m644 "$root/README.md" "$stage/usr/share/doc/zeromouse-cursor-theme/README.md"
cat > "$stage/DEBIAN/control" <<CONTROL
Package: zeromouse-cursor-theme
Version: $version
Section: x11
Priority: optional
Architecture: all
Maintainer: ZeroMouse contributors <zeromouse@users.noreply.github.com>
Suggests: adwaita-icon-theme
Description: High-visibility neon XCursor theme for people with low vision
 Neon lime and yellow-green cursor artwork, including animated busy and
 launch feedback cursors. Supports cursor images from 24 through 512 pixels.
CONTROL
dpkg-deb --root-owner-group --build "$stage" \
  "$out_dir/zeromouse-cursor-theme_${version}_all.deb"
