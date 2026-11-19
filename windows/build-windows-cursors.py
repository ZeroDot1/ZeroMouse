#!/usr/bin/env python3
"""Build multi-resolution Windows CUR and ANI files from the shared artwork."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build  # noqa: E402

OUT = ROOT / "windows" / "cursors"
# The CUR directory stores each image dimension in one byte. Windows interprets
# zero as 256, so larger images cannot be represented in a standards-compliant
# Windows cursor file.
CUR_SIZES = (24, 32, 36, 48, 64, 72, 96, 128, 256)

STATIC = {
    "arrow.cur": "left_ptr",
    "hand.cur": "hand",
    "help.cur": "help",
    "ibeam.cur": "text",
    "move.cur": "move",
    "crosshair.cur": "crosshair",
    "not-allowed.cur": "not-allowed",
    "size-ns.cur": "ns-resize",
    "size-we.cur": "ew-resize",
    "size-nwse.cur": "nwse-resize",
    "size-nesw.cur": "nesw-resize",
    "up-arrow.cur": "up-arrow",
    "pencil.cur": "pencil",
    "zoom-in.cur": "zoom-in",
    "zoom-out.cur": "zoom-out",
}


def hotspot(kind: str, size: int) -> tuple[int, int]:
    if kind == "progress":
        return size // 2, round(size * 5 / 64)
    if kind == "watch":
        return size // 2, size // 2
    return build.static[kind][1](size)


def _dib_image(image) -> bytes:
    width, height = image.size
    rgba = image.convert("RGBA")
    xor_rows = bytearray()
    and_rows = bytearray()
    mask_stride = ((width + 31) // 32) * 4

    for y in range(height - 1, -1, -1):
        mask_row = bytearray(mask_stride)
        for x in range(width):
            r, g, b, a = rgba.getpixel((x, y))
            xor_rows.extend((b, g, r, a))
            if a == 0:
                mask_row[x // 8] |= 0x80 >> (x % 8)
        and_rows.extend(mask_row)

    header = struct.pack(
        "<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0,
        len(xor_rows) + len(and_rows), 0, 0, 0, 0,
    )
    return header + xor_rows + and_rows


def make_cur(kind: str, frames: tuple[int, ...] = (0,)) -> bytes:
    images = []
    for phase in frames:
        for size in CUR_SIZES:
            images.append((size, phase, _dib_image(build.render(kind, size, phase))))

    directory_size = 6 + 16 * len(images)
    offset = directory_size
    directory = bytearray()
    payload = bytearray()
    for size, _phase, image_data in images:
        hx, hy = hotspot(kind, size)
        dimension = 0 if size == 256 else size
        directory.extend(struct.pack(
            "<BBBBHHII", dimension, dimension, 0, 0, hx, hy,
            len(image_data), offset,
        ))
        payload.extend(image_data)
        offset += len(image_data)

    return struct.pack("<HHH", 0, 2, len(images)) + directory + payload


def chunk(tag: bytes, body: bytes) -> bytes:
    result = tag + struct.pack("<I", len(body)) + body
    if len(body) & 1:
        result += b"\0"
    return result


def make_ani(kind: str, frame_count: int, frame_ms: int) -> bytes:
    frame_files = [make_cur(kind, (frame,)) for frame in range(frame_count)]
    default_jiffies = max(1, round(frame_ms * 60 / 1000))
    header = struct.pack(
        "<9I", 36, frame_count, frame_count, 0, 0, 0, 0,
        default_jiffies, 1,  # AF_ICON: each frame is a CUR image.
    )
    rates = struct.pack("<" + "I" * frame_count, *([default_jiffies] * frame_count))
    sequence = struct.pack("<" + "I" * frame_count, *range(frame_count))
    frame_list = b"fram" + b"".join(chunk(b"icon", data) for data in frame_files)
    form = (
        b"ACON"
        + chunk(b"anih", header)
        + chunk(b"rate", rates)
        + chunk(b"seq ", sequence)
        + chunk(b"LIST", frame_list)
    )
    return b"RIFF" + struct.pack("<I", len(form)) + form


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, artwork in STATIC.items():
        (OUT / filename).write_bytes(make_cur(artwork))
    (OUT / "wait.ani").write_bytes(make_ani("watch", frame_count=6, frame_ms=110))
    (OUT / "appstarting.ani").write_bytes(make_ani("progress", frame_count=4, frame_ms=100))
    print(f"Built {len(STATIC)} multi-resolution CUR files and 2 ANI files in {OUT}")


if __name__ == "__main__":
    main()
