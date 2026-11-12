# ZeroMouse Neon Launch

**Ein kontrastreiches XCursor-Thema für Menschen mit Sehbehinderungen und
schlechtem Sehvermögen.** Das Design entstand aus eigener Alltagserfahrung mit
Sehbehinderung und setzt auf leuchtendes Neongrün bis Gelbgrün, dunkle Konturen,
gut unterscheidbare Formen und große Cursorgrößen.

![Vorschau des ZeroMouse-Themas](preview/zeromouse-preview.png)

[Sanduhr-Animation](preview/hourglass-animation.gif) · [Raketenstart-Animation](preview/rocket-animation.gif) · [English README](README.en.md)

## Barrierearme Merkmale

- Zehn Cursorgrößen von 24 bis 512 Pixel, einschließlich 36 und 72 Pixel für
  gängige KDE-Größen.
- Helle, gelbgrüne Flächen mit dunkler Kontur zur Abgrenzung vor hellen und
  dunklen Oberflächen.
- Eigenständige Symbole für Zeiger, Text, Hand, Verschieben, Größenänderung,
  Hilfe, Zoom, Verbot und weitere häufige Cursorrollen.
- Animierte Sanduhr für Wartezeiten und Rakete als Fortschrittsanzeige.

Farbe und Größe lassen sich in unterstützten Desktopumgebungen anpassen. Die
Wahrnehmbarkeit hängt von Bildschirm, Skalierung, Hintergrund und individuellen
Sehbedürfnissen ab.

## Linux-Unterstützung und Pakete

Das Thema verwendet das verbreitete XCursor-Format. Die Cursorbilder enthalten
mehrere Auflösungen in einer Datei; die Dateien unter `zeromouse/cursors/`
heißen deshalb wie die Cursorrollen (`left_ptr`, `watch` usw.) und haben keine
Dateiendung. PNG und GIF in `preview/` sind separate Vorschaudateien.

Der Workflow **Build Linux packages** baut auf manuelle Anforderung in GitHub
Actions folgende Downloads:

| Systemfamilie | Paket |
| --- | --- |
| Arch Linux, CachyOS und andere Arch-basierte Systeme | pacman `.pkg.tar.zst` |
| Debian und Ubuntu | `.deb` |
| Fedora und RPM-basierte Systeme | `.rpm` |
| Andere Linux-Distributionen | portables XCursor-Archiv `.tar.gz` |

Wayland-Unterstützung hängt von Desktopumgebung und Compositor ab. KDE Plasma
und andere XCursor-kompatible Umgebungen können das Thema direkt auswählen.

## Pakete über GitHub bauen

1. Repository auf GitHub öffnen und **Actions → Build Linux packages → Run
   workflow** wählen.
2. Der Lauf erstellt alle vier Pakete, SHA-256-Prüfsummen und stellt ein
   gemeinsames Bundle unter **Artifacts** zum Download bereit.
3. Optional **Create a GitHub Release** auswählen. Dann werden die Artefakte an
   ein Release mit dem Tag `v<VERSION>` angehängt. Ein bereits vorhandenes Tag
   wird nicht überschrieben.

Die einzige Quelle der Projektversion ist [VERSION](VERSION). Vor einer
Veröffentlichung diese Datei aktualisieren und `pkgrel` in `PKGBUILD` auf `1`
zurücksetzen. Bei Änderungen am Arch-Paket ohne neue Projektversion wird nur
`pkgrel` erhöht.

## Arch Linux installieren

```sh
./install.sh
```

Oder selbst bauen und installieren:

```sh
makepkg -f
sudo pacman -U "$(makepkg --packagelist | tail -n 1)"
```

Danach in KDE **Systemeinstellungen → Farben & Designs → Cursor** öffnen,
**ZeroMouse Neon Launch** auswählen und die gewünschte Größe einstellen.
Entfernen:

```sh
./uninstall.sh
```

## Debian, Fedora und andere Systeme

Das `.deb` lässt sich mit `sudo apt install ./zeromouse-cursor-theme_*.deb`, das
RPM mit `sudo dnf install --nogpgcheck ./zeromouse-cursor-theme-*.rpm`
installieren. Das veröffentlichte RPM ist nicht signiert; vergleiche vor der
Installation die SHA-256-Prüfsumme aus `SHA256SUMS`. Das portable Archiv enthält
Thema und Anleitung; für eine systemweite Installation
den Ordner `zeromouse` nach `/usr/share/icons/ZeroMouse` kopieren, für eine
Benutzerinstallation nach `~/.local/share/icons/ZeroMouse`.

## Entwickeln und Lizenz

`VERSION` wird von allen Paketbauern gelesen. `build.py` erzeugt die XCursor-
Dateien; `preview.py` rendert die README-Vorschauen. Beide benötigen Python 3
und Pillow.

Das Projekt steht unter **GNU Affero General Public License v3.0 or later**
(AGPL-3.0-or-later). Siehe [LICENSE](LICENSE) und [CONTRIBUTING.md](CONTRIBUTING.md).
