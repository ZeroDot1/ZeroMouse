#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="$(tr -d '\r\n' < "$root/VERSION")"
out_dir="${1:-$root/dist}"
top="$(mktemp -d)"
trap 'rm -rf "$top"' EXIT

mkdir -p "$out_dir" "$top/BUILD" "$top/BUILDROOT" "$top/RPMS" \
  "$top/SOURCES/zeromouse" "$top/SPECS" "$top/SRPMS"
cp -a "$root/zeromouse/." "$top/SOURCES/zeromouse/"
cp -a "$root/LICENSE" "$root/README.md" "$top/SOURCES/zeromouse/"
cp -a "$root/preview" "$top/SOURCES/zeromouse/"
tar -czf "$top/SOURCES/zeromouse.tar.gz" -C "$top/SOURCES" zeromouse
rpmbuild -bb "$root/packaging/rpm/zeromouse-cursor-theme.spec" \
  --define "_topdir $top" --define "_rpmdir $top/RPMS" \
  --define "theme_version $version"
find "$top/RPMS" -type f -name '*.rpm' -exec cp -t "$out_dir" {} +
