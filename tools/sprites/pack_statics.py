#!/usr/bin/env python3
"""Pack swarm true-color statics into sheets, replace-in-place.
ONE scale per fighter (idle-raw -> old-idle-cell content height) so pose
heights stay natural. Keying: border-flood white; enclosed white with
near-black NEUTRAL ring = glowing eyes (keep); other enclosed white = blob
inpaint; low-sat gray bottom band = ground shadow (drop).
Usage: pack_statics.py <name> <cells...>
"""
import sys, json, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage

name = sys.argv[1]; wanted = sys.argv[2:]
REPO = pathlib.Path(__file__).resolve().parent.parent.parent
adir = REPO / "web" / "assets" / "sprites"
raw = REPO / "media" / "polished-candidates" / name / "truecolor-raw"
man = json.loads((adir / f"{name}.json").read_text())
sheet = Image.open(adir / f"{name}.png").convert("RGBA")
cellW, cellH, pad = man["frameW"], man["frameH"], man["frameH"] - man["footY"]

def keyed(img):
    a = np.array(img.convert("RGB"))
    bgcand = a.min(2) >= 205
    lbl, _ = ndimage.label(bgcand)
    border = np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))
    bg = np.isin(lbl, border[border != 0])
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    encl = bgcand & ~bg
    elbl, en = ndimage.label(encl)
    for k in range(1, en + 1):
        m = elbl == k
        if m.sum() < 15: continue
        ring = ndimage.binary_dilation(m, iterations=4) & ~bgcand
        if ring.sum() < 8: continue
        rp = a[ring].astype(int)
        if rp.mean() < 60 and (rp.max(1) - rp.min(1)).mean() < 22 and m.sum() < 2600: continue   # eyes are SMALL; big black-ringed whites are paint blobs
        a[m] = np.median(rp, axis=0).astype(np.uint8)
    h = a.shape[0]
    band = slice(int(h * 0.7), h)
    gray = (a[band].min(2) > 140) & (a[band].max(2).astype(int) - a[band].min(2) < 38)
    alpha[band][gray] = 0
    rgba = np.dstack([a, alpha])
    im = Image.fromarray(rgba)
    bb = im.getbbox()
    return im.crop(bb) if bb else im

# fighter scale anchor: old idle cell content height / idle raw content height
old_idle = sheet.crop((man["frames"]["idle"] * cellW, 0, (man["frames"]["idle"] + 1) * cellW, cellH))
bb = old_idle.getbbox(); target_h = bb[3] - bb[1]
idle_raw = keyed(Image.open(raw / "idle.png"))
k = target_h / idle_raw.height

packed = []
out = Image.new("RGBA", sheet.size, (0, 0, 0, 0)); out.paste(sheet, (0, 0))
for cell in wanted:
    src = raw / f"{cell}.png"
    if not src.exists() or cell not in man["frames"]:
        print(f"SKIP {cell} (missing raw or manifest slot)"); continue
    f = keyed(Image.open(src))
    f = f.resize((max(1, round(f.width * k)), max(1, round(f.height * k))), Image.LANCZOS)
    if f.width > cellW - 2 or f.height > cellH - pad - 2:
        s2 = min((cellW - 2) / f.width, (cellH - pad - 2) / f.height)
        f = f.resize((max(1, round(f.width * s2)), max(1, round(f.height * s2))), Image.LANCZOS)
    col = man["frames"][cell]
    out.paste(Image.new("RGBA", (cellW, cellH), (0, 0, 0, 0)), (col * cellW, 0))
    out.paste(f, (col * cellW + (cellW - f.width) // 2, cellH - pad - f.height), f)
    packed.append(cell)
out.save(adir / f"{name}.png", optimize=True)
print(f"{name}: packed {packed} (k={k:.3f})")
