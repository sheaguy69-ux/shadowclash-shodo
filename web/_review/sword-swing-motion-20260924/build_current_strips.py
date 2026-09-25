"""Extract the current packed sword cells for owner review; no runtime writes."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
WEB = ROOT.parent.parent
ATLAS = WEB / "assets" / "runtime-sprites"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
TITLE = ImageFont.truetype(FONT, 28)
SMALL = ImageFont.truetype(FONT, 17)


def strip(fighter, prefix, count, live_count, title):
    packed = json.loads((ATLAS / f"{fighter}.json").read_text())
    man = packed["sourceManifest"]
    pages = [Image.open(ATLAS / file).convert("RGBA") for file in packed["pages"]]
    cells = []
    names = []
    for i in range(1, count + 1):
        name = f"{prefix}{i}"
        idx = man["frames"][name]
        page, x, y, w, h, ox, oy = packed["cells"][idx]
        crop = pages[page].crop((x, y, x + w, y + h))
        cell = Image.new("RGBA", (man["frameW"], man["frameH"]))
        cell.paste(crop, (ox, oy), crop)
        cells.append(cell)
        names.append((name, idx))

    # Fixed crop across the complete source row preserves pose-to-pose spacing.
    boxes = [cell.getchannel("A").getbbox() for cell in cells]
    boxes = [b for b in boxes if b]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
           max(b[2] for b in boxes), max(b[3] for b in boxes))
    pad = 14
    box = (max(0, box[0] - pad), max(0, box[1] - pad),
           min(man["frameW"], box[2] + pad), min(man["frameH"], box[3] + pad))
    tile_w, tile_h, gap, margin = 228, 290, 12, 28
    canvas = Image.new("RGB", (margin * 2 + count * tile_w + (count - 1) * gap, 385), "#171b18")
    d = ImageDraw.Draw(canvas)
    d.text((margin, 18), title, font=TITLE, fill="#f5efe2")
    for i, (cell, (name, idx)) in enumerate(zip(cells, names)):
        x = margin + i * (tile_w + gap)
        y = 70
        active = i < live_count
        d.rounded_rectangle((x, y, x + tile_w, y + tile_h), radius=12,
                            fill="#e8dfca" if active else "#b8baa9",
                            outline="#c6a767" if active else "#737b70", width=3)
        crop = cell.crop(box)
        crop.thumbnail((tile_w - 14, tile_h - 64), Image.Resampling.LANCZOS)
        canvas.paste(crop, (x + (tile_w - crop.width) // 2,
                            y + 39 + (tile_h - 67 - crop.height) // 2), crop)
        d.text((x + 11, y + 10), f"{name}  ·  cell {idx}", font=SMALL, fill="#222a22")
        if not active:
            d.text((x + 11, y + tile_h - 30), "source only", font=SMALL, fill="#665e4e")
    canvas.save(ROOT / f"current-{fighter}-{prefix}.png")
    return {"fighter": fighter, "row": prefix, "source_cells": names,
            "live_count": live_count, "shared_crop": box}


rows = [
    strip("executioner", "xnuki", 6, 6, "EXECUTIONER  /  current grounded light"),
    strip("executioner", "xjodan", 8, 6, "EXECUTIONER  /  current neutral heavy; last two source cells unused"),
    strip("kael", "kdual", 8, 8, "KAEL  /  current grounded light"),
    strip("kael", "kcross", 8, 8, "KAEL  /  current neutral heavy"),
]
(ROOT / "source-mapping.json").write_text(json.dumps(rows, indent=2) + "\n")
