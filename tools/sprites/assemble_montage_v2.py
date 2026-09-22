#!/usr/bin/env python3
"""Assemble Mizu FINAL-candidate-montage.png v2 from verified-clean statics + i2v clips."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = "media/polished-candidates/mizu"
RAW = f"{BASE}/mizu/raw"
OUT = f"{BASE}/FINAL-candidate-montage.png"

CELL_W, CELL_H = 192, 214
LABEL_H = 28
COLS = 6
ROWS = 7

statics = sorted([n for n in os.listdir(RAW) if n.endswith(".png")])
statics = [n[:-4] for n in statics]

sprint_frames = ["f_019", "f_025", "f_031", "f_037", "f_049"]
staff_frames = ["f_019", "f_031", "f_049", "f_061", "f_073"]

# Build cell specs: (label, image_path)
cells = []
for name in statics:
    cells.append((name, f"{RAW}/{name}.png"))
for f in sprint_frames:
    cells.append((f"sprint-{f}", f"media/polished-candidates/mizu-i2v/sprint-v2/frames/{f}.png"))
for f in staff_frames:
    cells.append((f"staff-{f}", f"media/polished-candidates/mizu-i2v/staff-attack/frames/{f}.png"))
cells.append(("LIGHT/KICK FROZEN", None))

# Pad to fill grid
while len(cells) < COLS * ROWS:
    cells.append(("", None))

img = Image.new("RGBA", (COLS * CELL_W, ROWS * CELL_H), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
except Exception:
    font = ImageFont.load_default()

for idx, (label, path) in enumerate(cells):
    cx, cy = idx % COLS, idx // COLS
    x, y = cx * CELL_W, cy * CELL_H

    # White background cell
    draw.rectangle([x, y, x + CELL_W, y + CELL_H], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255))

    if path and os.path.exists(path):
        src = Image.open(path).convert("RGBA")
        # Key white background to transparent
        data = src.getdata()
        new_data = []
        for r, g, b, a in data:
            if r > 240 and g > 240 and b > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((r, g, b, a))
        src.putdata(new_data)

        bbox = src.getbbox()
        if bbox:
            src = src.crop(bbox)
            # Scale to fit inside cell with padding for label
            avail_w = CELL_W - 8
            avail_h = CELL_H - LABEL_H - 8
            scale = min(avail_w / src.width, avail_h / src.height)
            nw = max(1, int(src.width * scale))
            nh = max(1, int(src.height * scale))
            src = src.resize((nw, nh), Image.Resampling.LANCZOS)
            px = x + (CELL_W - nw) // 2
            py = y + LABEL_H + (avail_h - nh) // 2
            img.paste(src, (px, py), src)

    # Label
    if label:
        draw.text((x + 4, y + 4), label, fill=(0, 0, 0, 255), font=font)

img.save(OUT)
print(f"Saved {OUT}: {img.size}, {len([c for c in cells if c[1]])} image cells")
