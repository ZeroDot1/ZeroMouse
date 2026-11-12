pkgname=zeromouse-cursor-theme
pkgver="$(tr -d '\r\n' < "$startdir/VERSION")"
pkgrel=6
pkgdesc='High-visibility neon XCursor theme for people with low vision'
arch=('any')
license=('AGPL-3.0-or-later')
depends=()
optdepends=('adwaita-cursors: fallback cursors for unprovided cursor roles')
options=('!strip')

package() {
  install -dm755 "$pkgdir/usr/share/icons/ZeroMouse"
  cp -a "$startdir/zeromouse/." "$pkgdir/usr/share/icons/ZeroMouse/"
  install -Dm644 "$startdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
