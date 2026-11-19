#!/usr/bin/env python3
"""Validate ZeroMouse XCursor headers, sizes, hotspots, frames, and aliases."""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
CURSORS = ROOT / "zeromouse" / "cursors"
MAGIC = 0x72756358
IMAGE_TYPE = 0xFFFD0002
VERSION = 0x00010000
SIZES = (24, 32, 36, 48, 64, 72, 96, 128, 256, 512)
FRAME_COUNTS = {"watch": 6, "progress": 4}
ARTWORK = {
    "left_ptr", "hand", "text", "move", "ew-resize", "ns-resize",
    "nwse-resize", "nesw-resize", "crosshair", "not-allowed", "help",
    "zoom-in", "zoom-out", "pencil", "watch", "progress",
    "up-arrow", "grab", "grabbing", "vertical-text", "copy", "link",
    "context-menu", "blank",
}
REQUIRED_ROLES = {
    "default", "left_ptr", "pointer", "hand", "text", "xterm", "watch",
    "wait", "progress", "left_ptr_watch", "move", "fleur", "ew-resize",
    "ns-resize", "nwse-resize", "nesw-resize", "crosshair", "not-allowed",
    "help", "question_arrow", "zoom-in", "zoom-out", "pencil", "copy",
    "link", "grab", "grabbing", "dnd-move", "dnd-no-drop", "cell",
    "color-picker", "size_hor", "size_ver", "size_fdiag", "size_bdiag",
    "top_left_corner", "bottom_right_corner", "wayland-cursor",
    "up_arrow", "left_arrow", "blank", "dnd-ask", "bd_double_arrow",
    "fd_double_arrow", "all-resize", "cross_reverse", "wayland_cursor",
}

def fail(message):
    raise SystemExit(f"XCursor validation failed: {message}")

def validate_file(path):
    data = path.read_bytes()
    if len(data) < 16:
        fail(f"{path.name}: file is shorter than the XCursor header")
    magic, header_size, version, count = struct.unpack_from("<IIII", data)
    if (magic, header_size, version) != (MAGIC, 16, VERSION):
        fail(f"{path.name}: invalid XCursor 1.0 header")
    table_end = header_size + count * 12
    if count == 0 or table_end > len(data):
        fail(f"{path.name}: invalid table of contents")

    actual_sizes = []
    chunks = []
    for index in range(count):
        cursor_type, subtype, position = struct.unpack_from("<III", data, header_size + index * 12)
        if cursor_type != IMAGE_TYPE or position < table_end or position + 36 > len(data):
            fail(f"{path.name}: invalid image entry {index}")
        chunk_header, chunk_type, chunk_size, chunk_version, width, height, hot_x, hot_y, delay = struct.unpack_from(
            "<IIIIIIIII", data, position
        )
        end = position + chunk_header + width * height * 4
        if (chunk_header, chunk_type, chunk_version) != (36, IMAGE_TYPE, 1):
            fail(f"{path.name}: invalid image chunk {index}")
        if width != subtype or height != subtype or width not in SIZES:
            fail(f"{path.name}: invalid dimensions in image chunk {index}")
        if hot_x >= width or hot_y >= height or end > len(data):
            fail(f"{path.name}: invalid hotspot or truncated pixels in image chunk {index}")
        pixels = memoryview(data)[position + 36:end]
        if any(pixels[3::4]) == (path.name == "blank"):
            fail(f"{path.name}: unexpected image transparency in chunk {index}")
        actual_sizes.append(subtype)
        chunks.append((position, end, delay))

    expected_frames = FRAME_COUNTS.get(path.name, 1)
    expected_order = list(SIZES) * expected_frames
    if actual_sizes != expected_order:
        fail(f"{path.name}: expected {expected_frames} frame(s) at all ten sizes")
    for index, (_, _, delay) in enumerate(chunks):
        if (expected_frames > 1 and delay == 0) or (expected_frames == 1 and delay != 0):
            fail(f"{path.name}: incorrect frame delay at image {index}")

    intervals = sorted((start, end) for start, end, _ in chunks)
    for previous, current in zip(intervals, intervals[1:]):
        if previous[1] > current[0]:
            fail(f"{path.name}: image chunks overlap")

def main():
    if not CURSORS.is_dir():
        fail("cursor directory is missing")
    entries = {p.name: p for p in CURSORS.iterdir()}
    missing = REQUIRED_ROLES - entries.keys()
    if missing:
        fail("missing cursor roles: " + ", ".join(sorted(missing)))
    for name, path in entries.items():
        if path.is_symlink():
            target = (CURSORS / path.readlink()).resolve()
            if not target.is_file() or target.parent != CURSORS.resolve():
                fail(f"{name}: broken or out-of-theme alias")
        elif path.is_file():
            validate_file(path)
        else:
            fail(f"{name}: unsupported filesystem entry")
    artwork = {name for name, path in entries.items() if path.is_file() and not path.is_symlink()}
    if artwork != ARTWORK:
        fail("unexpected artwork files: " + ", ".join(sorted(artwork ^ ARTWORK)))
    print(f"Validated {len(artwork)} XCursor images and {len(entries) - len(artwork)} aliases.")

if __name__ == "__main__":
    main()
