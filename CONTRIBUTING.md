# Mitwirken / Contributing

ZeroMouse is an accessibility-focused cursor theme. Contributions that improve
legibility, cursor-role coverage, KDE behavior, and compatibility are welcome.

## Fehler melden

Bitte beschreibe Betriebssystem und Version, Desktopumgebung, X11 oder Wayland,
Skalierungsfaktor, ausgewählte Cursorgröße, betroffene Cursorrolle und die
Schritte zum Nachstellen. Ein Screenshot kann helfen. Persönliche Gesundheits-
oder Diagnosedaten sind nicht nötig.

## Änderungen testen

- `python3 build.py` regeneriert die XCursor-Dateien.
- `python3 preview.py` aktualisiert PNG- und GIF-Vorschauen.
- Auf Arch Linux: `makepkg -f` baut das pacman-Paket.
- Der Workflow **Build Linux packages** prüft die Paketformate für Arch,
  Debian/Ubuntu, Fedora und ein portables Linux-Archiv.

Bitte behalte `VERSION` als einzige Quelle der Projektversion. Wenn sich das
Arch-Paket ohne neue Projektversion ändert, erhöhe zusätzlich `pkgrel` in
`PKGBUILD`. Bei einer neuen Projektversion setze `pkgrel` auf `1` zurück.

## Contributing in English

ZeroMouse is an accessibility-focused cursor theme. Bug reports should include
the OS and version, desktop environment, X11 or Wayland, display scaling,
selected cursor size, affected cursor role, and reproduction steps. A screenshot
can help. Please do not include personal health or diagnosis information.

Run `python3 build.py` and `python3 preview.py` after artwork changes. On Arch,
`makepkg -f` builds the pacman package. The manually triggered GitHub Actions
workflow builds the Arch, Debian/Ubuntu, Fedora, and portable Linux artifacts.
Use `VERSION` as the single project version source; increase Arch `pkgrel` when
the PKGBUILD changes without a project version bump. Reset `pkgrel` to `1` for
a new project version.
