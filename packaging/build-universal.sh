#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="$(tr -d '\r\n' < "$root/VERSION")"
out_dir="${1:-$root/dist}"
mkdir -p "$out_dir"
tar -czf "$out_dir/zeromouse-cursor-theme-${version}-linux-any.tar.gz" \
  --exclude='./.git' --exclude='./dist' --exclude='./pkg' --exclude='./src' \
  --exclude='./*.pkg.tar.zst' --exclude='./*.deb' --exclude='./*.rpm' \
  --exclude='./*.apk' \
  -C "$root" .
