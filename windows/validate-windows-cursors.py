#!/usr/bin/env python3
"""Check Windows CUR/ANI structure, image sizes, hotspots, and frame timing."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CURSORS = ROOT / "cursors"
SIZES = (24, 32, 36, 48, 64, 72, 96, 128, 256)
STATIC_FILES = {
    "arrow.cur", "hand.cur", "help.cur", "ibeam.cur", "move.cur",
    "crosshair.cur", "not-allowed.cur", "size-ns.cur", "size-we.cur",
    "size-nwse.cur", "size-nesw.cur", "up-arrow.cur", "pencil.cur",
    "zoom-in.cur", "zoom-out.cur",
}


def fail(message: str) -> None:
    raise SystemExit(f"Windows cursor validation failed: {message}")


def validate_cur(data: bytes, name: str) -> list[int]:
    if len(data) < 6:
        fail(f"{name}: truncated CUR directory")
    reserved, file_type, count = struct.unpack_from("<HHH", data)
    if reserved != 0 or file_type != 2 or count == 0:
        fail(f"{name}: invalid CUR header")
    directory_end = 6 + 16 * count
    if directory_end > len(data):
        fail(f"{name}: truncated CUR directory entries")

    sizes = []
    for index in range(count):
        entry = struct.unpack_from("<BBBBHHII", data, 6 + index * 16)
        width, height, colors, reserved, hot_x, hot_y, byte_count, offset = entry
        width = width or 256
        height = height or 256
        if reserved or colors or width != height or width not in SIZES:
            fail(f"{name}: invalid dimensions or directory flags in image {index}")
        if hot_x >= width or hot_y >= height:
            fail(f"{name}: invalid hotspot in image {index}")
        end = offset + byte_count
        if offset < directory_end or end > len(data) or byte_count < 40:
            fail(f"{name}: invalid image offset or length in image {index}")
        header = struct.unpack_from("<IiiHHIIiiII", data, offset)
        header_size, dib_width, dib_height, planes, bpp, compression, image_bytes = header[:7]
        if (header_size, dib_width, dib_height, planes, bpp, compression) != (
            40, width, height * 2, 1, 32, 0
        ):
            fail(f"{name}: invalid 32-bit DIB image {index}")
        mask_stride = ((width + 31) // 32) * 4
        expected_bytes = width * height * 4 + mask_stride * height
        if image_bytes != expected_bytes or byte_count != 40 + expected_bytes:
            fail(f"{name}: incorrect XOR/AND mask length in image {index}")
        pixels = data[offset + 40:offset + 40 + width * height * 4]
        if not any(pixels[3::4]):
            fail(f"{name}: fully transparent image {index}")
        sizes.append(width)

    if sizes != list(SIZES):
        fail(f"{name}: expected sizes {SIZES}, got {sizes}")
    return sizes


def read_chunks(data: bytes, start: int, limit: int):
    position = start
    while position + 8 <= limit:
        tag = data[position:position + 4]
        length = struct.unpack_from("<I", data, position + 4)[0]
        body_start = position + 8
        body_end = body_start + length
        if body_end > limit:
            fail("ANI chunk exceeds its containing list")
        yield tag, data[body_start:body_end]
        position = body_end + (length & 1)
    if position != limit:
        fail("ANI chunk list has trailing or truncated bytes")


def validate_ani(path: Path, expected_frames: int) -> None:
    data = path.read_bytes()
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"ACON":
        fail(f"{path.name}: invalid RIFF/ACON header")
    if struct.unpack_from("<I", data, 4)[0] + 8 != len(data):
        fail(f"{path.name}: RIFF length does not match file")

    top_chunks = list(read_chunks(data, 12, len(data)))
    chunks = {tag: body for tag, body in top_chunks}
    header = chunks.get(b"anih")
    rates = chunks.get(b"rate")
    sequence = chunks.get(b"seq ")
    frame_list = chunks.get(b"LIST")
    if header is None or len(header) != 36 or rates is None or sequence is None or frame_list is None:
        fail(f"{path.name}: missing required ANI chunks")
    fields = struct.unpack("<9I", header)
    size, frames, steps, width, height, bit_count, planes, default_rate, flags = fields
    if (size, frames, steps, width, height, bit_count, planes, flags) != (
        36, expected_frames, expected_frames, 0, 0, 0, 0, 1
    ) or default_rate == 0:
        fail(f"{path.name}: invalid ANI header")
    if len(rates) != 4 * steps or len(sequence) != 4 * steps:
        fail(f"{path.name}: incorrect ANI rate or sequence table")
    if tuple(struct.unpack("<" + "I" * steps, sequence)) != tuple(range(frames)):
        fail(f"{path.name}: invalid ANI frame sequence")
    frame_count = struct.unpack_from("<I", frame_list, 0)[0]
    if frame_count != int.from_bytes(b"fram", "little"):
        fail(f"{path.name}: missing ANI frame list type")
    icons = list(read_chunks(frame_list, 4, len(frame_list)))
    if len(icons) != frames or any(tag != b"icon" for tag, _ in icons):
        fail(f"{path.name}: expected {frames} ANI cursor frames")
    for index, (_, cur_data) in enumerate(icons):
        validate_cur(cur_data, f"{path.name} frame {index}")
    frame_rates = struct.unpack("<" + "I" * steps, rates)
    if any(rate == 0 for rate in frame_rates):
        fail(f"{path.name}: zero-length frame")


def main() -> None:
    actual = {path.name for path in CURSORS.iterdir()}
    expected = STATIC_FILES | {"wait.ani", "appstarting.ani"}
    if actual != expected:
        fail(f"unexpected files: {sorted(actual ^ expected)}")
    for name in sorted(STATIC_FILES):
        validate_cur((CURSORS / name).read_bytes(), name)
    validate_ani(CURSORS / "wait.ani", 6)
    validate_ani(CURSORS / "appstarting.ani", 4)
    print(f"Validated {len(STATIC_FILES)} multi-resolution CUR files and 2 ANI animations.")


if __name__ == "__main__":
    main()
