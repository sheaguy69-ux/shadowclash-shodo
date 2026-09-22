#!/usr/bin/env python3
"""Pack 8 harvested i2v frames as run_clean1-8 with TRUE registered geometry:
ONE shared crop window (union ink bbox), ONE scale factor, in-window offsets
preserved (natural bob + stride geometry survive). Frames are mirrored to face
right. The clip's soft drop-shadow is killed by brightness keying inside the window.

Usage: [KEY_PREFIX=run_clean] [SOURCE_FMT='f_{n:03d}.png']
       pack_i2v8.py <name> <frames_dir> <f1> ... <f8>
"""
import sys, json, pathlib, os
import numpy as np
from PIL import Image, ImageOps

name, fdir = sys.argv[1], sys.argv[2]
picks = [int(x) for x in sys.argv[3:11]]
key_prefix = os.environ.get("KEY_PREFIX", "run_clean")
source_fmt = os.environ.get("SOURCE_FMT", "f_{n:03d}.png")
REPO = pathlib.Path(__file__).resolve().parent.parent.parent
adir = REPO / "web" / "assets" / "sprites"
man = json.loads((adir / f"{name}.json").read_text())
sheet = Image.open(adir / f"{name}.png").convert("RGBA")
cellW, cellH, pad = man["frameW"], man["frameH"], man["frameH"] - man["footY"]

raws = [Image.open(pathlib.Path(fdir) / source_fmt.format(n=n)).convert("RGB") for n in picks]
# MIRROR=1: the source clip faces the WRONG way (the i2v model ignored "facing LEFT" on
# some run clips) — flip every frame so the packed run matches the left-facing
# statics + the engine's ctx.scale(-facing,1) convention. Order/offsets preserved.
if os.environ.get('MIRROR'):
    raws = [ImageOps.mirror(im) for im in raws]
# shared window = union ink bbox (ink = clearly darker than bg/shadow)
x0, y0, x1, y1 = 10**9, 10**9, 0, 0
for im in raws:
    a = np.array(im)
    ys, xs = np.where(a.min(2) < 130)   # character ink only — soft shadow (~150-205) must not stretch the window
    x0, y0 = min(x0, xs.min()), min(y0, ys.min())
    x1, y1 = max(x1, xs.max()), max(y1, ys.max())
x0, y0, x1, y1 = max(0, x0-6), max(0, y0-6), x1+6, y1+6

cells = []
for im in raws:
    a = np.array(im.crop((x0, y0, x1, y1)))
    from scipy import ndimage
    bgcand = a.min(2) >= 205
    # only border-connected white is background — enclosed white (glowing eyes!) stays opaque
    lbl, n = ndimage.label(bgcand)
    border = np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))
    bg = np.isin(lbl, border[border != 0])
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    # enclosed white: black ring = glowing eye (keep); colored ring = paint blob (inpaint)
    encl = bgcand & ~bg
    elbl, en = ndimage.label(encl)
    for k in range(1, en + 1):
        m = elbl == k
        if m.sum() < 15: continue
        ring = ndimage.binary_dilation(m, iterations=4) & ~bgcand
        if ring.sum() < 8: continue
        ringpx = a[ring].astype(int)
        neutral = (ringpx.max(1) - ringpx.min(1)).mean() < 22
        if ringpx.mean() < 60 and neutral and m.sum() < 2600: continue   # near-black NEUTRAL ring + eye-sized -> glowing eye (big blobs inpaint)
        a[m] = np.median(ringpx, axis=0).astype(np.uint8)
    # the clip's soft ground shadow: low-sat mid-gray in the bottom band
    h = a.shape[0]
    band = slice(int(h*0.62), h)
    # >140 missed the DARKER cast shadows the wave-2 clips bake in, which then
    # flicker on/off between run cells. Character darks sit far below 95
    # (charcoal boots ~40), so 95 keeps safe headroom.
    gray = (a[band].min(2) > 95) & (a[band].max(2).astype(int) - a[band].min(2) < 44)
    alpha[band][gray] = 0
    alpha[:, :4] = 0; alpha[:, -4:] = 0; alpha[:4] = 0; alpha[-4:] = 0   # window-edge junk
    rgba = np.dstack([a, alpha])
    cells.append(Image.fromarray(rgba))   # LEFT-facing = engine convention

# one scale: window height -> old run cell content height (keeps game scale)
# size anchor = IDLE cell (owner: characters must not shrink when they move)
rc = sheet.crop((man["frames"]["idle"]*cellW, 0, (man["frames"]["idle"]+1)*cellW, cellH))
bb = rc.getbbox(); target_h = int((bb[3]-bb[1]) * 0.94) if bb else cellH - pad - 20
s = min(target_h / cells[0].height, (cellW-2) / cells[0].width)
cells = [c.resize((max(1, round(c.width*s)), max(1, round(c.height*s))), Image.LANCZOS) for c in cells]

need = sum(1 for i in range(1, 9) if f"{key_prefix}{i}" not in man["frames"])
out = Image.new("RGBA", (cellW*(man["cols"]+need), cellH), (0,0,0,0))
out.paste(sheet, (0, 0))
nxt = man["cols"]
for i, c in enumerate(cells, 1):
    key = f"{key_prefix}{i}"
    col = man["frames"].get(key)
    if col is None:
        col = nxt; nxt += 1; man["frames"][key] = col
    out.paste(Image.new("RGBA", (cellW, cellH), (0,0,0,0)), (col*cellW, 0))
    # in-window offsets preserved: same paste origin for every frame
    out.paste(c, (col*cellW + (cellW-c.width)//2, cellH - pad - c.height), c)
man["cols"] = nxt
out.save(adir / f"{name}.png", optimize=True)
(adir / f"{name}.json").write_text(json.dumps(man))
print(f"packed {name} {key_prefix}1-8 from {picks}, scale {s:.3f}, cols {man['cols']}")
