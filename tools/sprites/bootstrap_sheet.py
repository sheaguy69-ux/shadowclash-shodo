#!/usr/bin/env python3
"""Create a NEW fighter's sheet + manifest from their truecolor-raw statics.

pack_statics/pack_cells/pack_i2v8 all pack INTO an existing sheet and scale
against its idle cell — so a brand-new fighter needs this one-time bootstrap.
Same keying stack as the other packers (border-flood bg, eye-preserving
enclosed white, blob inpaint, shadow band, edge clear), and the roster's
fixed cell geometry (frameH 226 / footY 218) so the new fighter stands at
the same scale as the existing six.

Usage: bootstrap_sheet.py <name> [cells...]   (default: the 9 standard statics)
"""
import sys, json, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage

name = sys.argv[1]
cells = sys.argv[2:] or ["idle", "idle2", "jump", "fall", "kneel", "roll", "hurt", "block", "wallslide"]
REPO = pathlib.Path(__file__).resolve().parent.parent.parent
adir = REPO / "web" / "assets" / "sprites"
raw = REPO / "media" / "polished-candidates" / name / "truecolor-raw"

CELL_H, FOOT_Y = 226, 218          # roster-fixed: every fighter shares the floor line
BODY_H = 150                       # idle content height -> matches the existing six on screen
pad = CELL_H - FOOT_Y

def keyed(img):
    a = np.array(img.convert("RGB"))
    bgcand = a.min(2) >= 205
    lbl, _ = ndimage.label(bgcand)
    border = np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))
    bg = np.isin(lbl, border[border != 0])
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    # enclosed white: near-black NEUTRAL ring + eye-sized = glowing eyes (keep); else inpaint
    encl = bgcand & ~bg
    elbl, en = ndimage.label(encl)
    for k in range(1, en + 1):
        m = elbl == k
        if m.sum() < 15: continue
        ring = ndimage.binary_dilation(m, iterations=4) & ~bgcand
        if ring.sum() < 8: continue
        rp = a[ring].astype(int)
        if rp.mean() < 60 and (rp.max(1) - rp.min(1)).mean() < 22 and m.sum() < 2600: continue
        a[m] = np.median(rp, axis=0).astype(np.uint8)
    h = a.shape[0]
    band = slice(int(h * 0.62), h)
    gray = (a[band].min(2) > 95) & (a[band].max(2).astype(int) - a[band].min(2) < 44)
    alpha[band][gray] = 0                      # ground-shadow strip
    alpha[:, :4] = 0; alpha[:, -4:] = 0; alpha[:4] = 0; alpha[-4:] = 0
    rgba = np.dstack([a, alpha])
    im = Image.fromarray(rgba)
    return im.crop(im.getbbox())

imgs = {}
for c in cells:
    p = raw / f"{c}.png"
    if not p.exists():
        print(f"  skip {c} (missing)"); continue
    imgs[c] = keyed(Image.open(p))

if "idle" not in imgs:
    sys.exit(f"{name}: no idle.png — cannot set scale")

# ONE scale for the whole fighter, driven by idle, so poses keep their relative size
s = BODY_H / imgs["idle"].height
scaled = {k: v.resize((max(1, round(v.width * s)), max(1, round(v.height * s))), Image.LANCZOS)
          for k, v in imgs.items()}
cellW = max(max(v.width for v in scaled.values()) + 8, 120)

order = [c for c in cells if c in scaled]
sheet = Image.new("RGBA", (cellW * len(order), CELL_H), (0, 0, 0, 0))
frames = {}
for i, c in enumerate(order):
    im = scaled[c]
    sheet.paste(im, (i * cellW + (cellW - im.width) // 2, CELL_H - pad - im.height), im)
    frames[c] = i

man = {"frameW": cellW, "frameH": CELL_H, "footY": FOOT_Y, "cols": len(order),
       # roster law: scale * idle-content-height == ~70px on screen, or the
       # engine multiplies by undefined and the fighter never draws (NaN).
       "scale": round(70.0 / BODY_H, 4), "frames": frames}
sheet.save(adir / f"{name}.png", optimize=True)
(adir / f"{name}.json").write_text(json.dumps(man))
print(f"bootstrapped {name}: {len(order)} cells, cellW {cellW}, scale {s:.3f} -> {order}")
