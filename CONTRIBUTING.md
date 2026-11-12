# Contributing

ZeroMouse is an accessibility-focused cursor theme. Contributions that improve
legibility, cursor-role coverage, KDE behavior, and compatibility are welcome.

## Reporting issues

Please include the operating system and version, desktop environment, X11 or
Wayland session, display scaling, selected cursor size, affected cursor role,
and steps to reproduce the issue. A screenshot can help. Personal health or
diagnosis information is not needed.

## Validating changes

- `python3 build.py` regenerates the XCursor files.
- `python3 scripts/validate-xcursor.py` checks headers, sizes, hotspots,
  animations, and alias targets.
- `python3 -m pip install -r requirements.txt` installs Pillow for artwork
  rendering and preview generation.
- On Arch Linux, `makepkg -f` builds the pacman package.
- The **Build Linux packages** workflow validates and builds packages for
  Arch, Debian/Ubuntu, Fedora, and other Linux distributions.

Use `VERSION` as the single source for the project version. When changing the
Arch package without a new project version, increase `pkgrel` in `PKGBUILD`. For
a new project version, reset `pkgrel` to `1`.
