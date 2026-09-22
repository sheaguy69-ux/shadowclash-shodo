#!/usr/bin/env python3
"""Append approved six-frame full-body attack strips to character sheets."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "web" / "assets" / "sprites"
GENERATED = Path(__file__).resolve().parent / "generated_attack6"
STRIPS = {
    "executioner": [("attack_body", "executioner-attack6.png")],
    "mizu": [("attack_body", "mizu-attack6.png")],
    "shin": [("attack_body", "shin-punch6.png"), ("flying_kick", "shin-flyingkick6.png")],
    "tsubasa": [("attack_body", "tsubasa-attack6.png")],
    "ember": [("attack_body", "ember-attack6.png")],
    "kael": [("attack_body", "kael-attack6.png")],
}

def split_cells(strip, count=6):
    return [strip.crop((round(i*strip.width/count), 0,
                        round((i+1)*strip.width/count), strip.height)) for i in range(count)]

def fitted_cells(strip, fw, fh, foot_y, target_h):
    cells = split_cells(strip)
    boxes = [c.getchannel("A").getbbox() for c in cells]
    valid = [b for b in boxes if b]
    top, bottom = min(b[1] for b in valid), max(b[3] for b in valid)
    scale = min(target_h/(bottom-top), (fw-4)/max(b[2]-b[0] for b in valid))
    output = []
    for cell, box in zip(cells, boxes):
        canvas = Image.new("RGBA", (fw, fh))
        if box:
            # Common vertical crop/scale preserves airborne height across the sequence.
            crop = cell.crop((box[0], top, box[2], bottom))
            crop = crop.resize((max(1, round(crop.width*scale)),
                                max(1, round(crop.height*scale))), Image.Resampling.LANCZOS)
            canvas.alpha_composite(crop, ((fw-crop.width)//2,
                                          max(0, min(fh-crop.height, foot_y-crop.height))))
        output.append(canvas)
    return output

def pack(name, entries):
    mp, sp = SPRITES/f"{name}.json", SPRITES/f"{name}.png"
    man = json.loads(mp.read_text()); sheet = Image.open(sp).convert("RGBA")
    fw, fh, frames = man["frameW"], man["frameH"], man["frames"]
    ref = frames["heavy1"]
    box = sheet.crop((ref*fw, 0, (ref+1)*fw, fh)).getchannel("A").getbbox()
    target_h = box[3]-box[1] if box else fh-12
    next_col = man["cols"]
    for prefix, _ in entries:
        start = frames.get(f"{prefix}1", next_col); next_col = max(next_col, start+6)
        for i in range(6): frames[f"{prefix}{i+1}"] = start+i
    packed = Image.new("RGBA", (next_col*fw, fh)); packed.paste(sheet, (0, 0))
    for prefix, filename in entries:
        cells = fitted_cells(Image.open(GENERATED/filename).convert("RGBA"),
                             fw, fh, man["footY"], target_h)
        for i, cell in enumerate(cells):
            idx = frames[f"{prefix}{i+1}"]
            packed.paste((0,0,0,0), (idx*fw,0,(idx+1)*fw,fh)); packed.alpha_composite(cell,(idx*fw,0))
    man["cols"] = next_col; packed.save(sp, optimize=True)
    mp.write_text(json.dumps(man, separators=(",", ":"))+"\n")
    print(f"{name}: {next_col} cells")

if __name__ == "__main__":
    for character, entries in STRIPS.items(): pack(character, entries)
