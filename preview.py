#!/usr/bin/env python3
"""Render README-ready PNG and GIF previews of the ZeroMouse cursor artwork."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import build

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "preview"
OUT.mkdir(exist_ok=True)
BG = (23, 29, 22)
FG = (221, 232, 205)

def font(size):
    for candidate in ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

names = ["left_ptr", "hand", "text", "move", "ew-resize", "ns-resize",
         "nwse-resize", "crosshair", "not-allowed", "help", "zoom-in",
         "zoom-out", "pencil", "watch", "progress"]
cell_w, cell_h, cols = 176, 150, 6
rows = (len(names) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), BG)
d = ImageDraw.Draw(sheet)
for i, name in enumerate(names):
    x, y = (i % cols) * cell_w, (i // cols) * cell_h
    icon = build.render(name, 88, 2)
    sheet.paste(icon, (x + (cell_w - 88)//2, y + 10), icon)
    label = name.replace("_", " ")
    box = d.textbbox((0, 0), label, font=font(14))
    d.text((x + (cell_w - (box[2]-box[0]))//2, y + 108), label, fill=FG, font=font(14))
sheet.save(OUT / "zeromouse-preview.png", optimize=True)

for name, frames, ms in (("hourglass", 6, 110), ("rocket", 4, 100)):
    images=[]
    kind = "watch" if name == "hourglass" else "progress"
    for phase in range(frames):
        icon=build.render(kind, 128, phase)
        frame=Image.new("RGBA", (176, 160), BG + (255,))
        frame.alpha_composite(icon, ((176-128)//2, 8))
        fd=ImageDraw.Draw(frame)
        label="Animated hourglass" if name == "hourglass" else "Rocket launch"
        fd.text((12, 140),label,fill=FG,font=font(12))
        images.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
    images[0].save(OUT / f"{name}-animation.gif", save_all=True, append_images=images[1:],
                   duration=ms, loop=0, optimize=True, disposal=2)
