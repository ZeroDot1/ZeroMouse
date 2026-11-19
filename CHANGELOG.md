
# Changelog

## 1.0.6

- Added cursor names used by Qt and Linux desktops, with dedicated artwork for
  grab, grabbing, copy, link, context menu, vertical text, and alternate select.
- Removed the explicit Adwaita fallback and packaged a transparent cursor for
  applications that ask to hide the pointer.
- Improved question mark contrast, resize arrow geometry, and rocket exhaust.
- Matched Windows cursor hotspots to the shared artwork.
- Limited the portable Linux archive to theme files, previews, and documentation.
- Made the Arch helper scripts check the built package and remove only ZeroMouse.

## 1.0.5

- Added multi-resolution Windows cursor files generated from the same artwork
  as the Linux XCursor theme.
- Added animated Windows hourglass and rocket cursors, plus a per-user installer
  that applies the Windows cursor scheme and restores the previous settings on
  uninstall.
- Extended the GitHub Actions package and release workflow to include a Windows
  installer.

## 1.0.0

- Initial public-ready release of the accessibility-focused ZeroMouse XCursor
  theme.
- Added ten multi-resolution sizes, KDE cursor-role aliases, and animated
  hourglass and rocket cursors.
- Refined artwork with antialiased rendering, a recognizable pointing hand, a
  legible question mark, corrected hourglass sand placement, and restrained
  rocket lift-off motion.
- Added Arch, Debian/Ubuntu, Fedora/RPM, and portable Linux package builds.
