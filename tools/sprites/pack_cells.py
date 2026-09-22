#!/usr/bin/env python3
"""Generic i2v cell packer: shared window + shared scale from a clip's frames.
Replaces existing cells in place, appends new ones. Same keying stack as
pack_i2v8 (border-flood bg, eye-preserving enclosed white, blob inpaint,
shadow band, edge clear). Mirrors to face right.
Usage: pack_cells.py <name> <frames_dir> cell=frameN [cell=frameN ...]
"""
import sys, json, pathlib
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

name, fdir = sys.argv[1], sys.argv[2]
pairs = [a.split("=") for a in sys.argv[3:]]
cellnames = [a for a, _ in pairs]
picks = [int(b) for _, b in pairs]

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
adir = REPO / "web" / "assets" / "sprites"
man = json.loads((adir / f"{name}.json").read_text())
sheet = Image.open(adir / f"{name}.png").convert("RGBA")
cellW, cellH, pad = man["frameW"], man["frameH"], man["frameH"] - man["footY"]

raws = [Image.open(f"{fdir}/f_{n:03d}.png").convert("RGB") for n in picks]
# INK_MAX: what counts as character ink for the crop window. Default 130 (dark
# ink only — keeps the clip's soft shadow from stretching the window). Characters
# with LIGHT-GRAY features at the silhouette edge (mokurai's stone mask crown)
# need ~200 or the window slices through the feature (the headless-jump class).
INK = int(__import__('os').environ.get('INK_MAX', 130))
x0, y0, x1, y1 = 10**9, 10**9, 0, 0
for im in raws:
    a = np.array(im)
    ys, xs = np.where(a.min(2) < INK)
    x0, y0 = min(x0, xs.min()), min(y0, ys.min())
    x1, y1 = max(x1, xs.max()), max(y1, ys.max())
x0, y0, x1, y1 = max(0, x0-6), max(0, y0-6), x1+6, y1+6

# BG_MIN: background-white floor for the flood key. Default 205. Bright feature
# highlights (mokurai's lit stone crown ~205-235) can bridge into the border white
# and get flood-removed with it — raise toward 240 for those frames.
BG = int(__import__('os').environ.get('BG_MIN', 205))
cells = []
for im in raws:
    a = np.array(im.crop((x0, y0, x1, y1)))
    bgcand = a.min(2) >= BG
    lbl, _n = ndimage.label(bgcand)
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
        if __import__('os').environ.get('ENCL_CLEAR'):
            # background enclosed by an FX ring (mokurai's halo) is SEE-THROUGH,
            # not a paint blob — clear it instead of inpainting a gray plate
            alpha[m] = 0
            continue
        a[m] = np.median(rp, axis=0).astype(np.uint8)
    if __import__('os').environ.get('DROP_GRAY'):
        # baked swipe-trails key badly (gray slabs). Steel weapons are ALSO gray —
        # but weapons wear a black OUTLINE, trails don't.
        graycand = (a.min(2) > 70) & (a.max(2).astype(int) - a.min(2) < 46)
        glbl, gn = ndimage.label(graycand)
        for gk in range(1, gn + 1):
            gm = glbl == gk
            if gm.sum() < 40: continue
            # backdrop shadow-walls touch the window edge; held weapons never do
            if gm[:6].any() or gm[-6:].any() or gm[:, :6].any() or gm[:, -6:].any():
                alpha[gm] = 0; continue
            gring = ndimage.binary_dilation(gm, iterations=2) & ~gm
            if gring.sum() < 10: continue
            if (a[gring].min(1) < 60).mean() < 0.22:
                alpha[gm] = 0
    h = a.shape[0]
    band = slice(int(h*0.72), h)
    gray = (a[band].min(2) > 140) & (a[band].max(2).astype(int) - a[band].min(2) < 38)
    alpha[band][gray] = 0
    alpha[:, :4] = 0; alpha[:, -4:] = 0; alpha[:4] = 0; alpha[-4:] = 0
    cells.append(Image.fromarray(np.dstack([a, alpha])))   # LEFT-facing = engine convention (ctx.scale(-facing) mirrors in-game)

# size anchor = IDLE cell (owner: "why do they get small when they run" — the old
# run cell was legacy-undersized; idle is the character's true size). 0.94: action
# poses lean, so their window is naturally a hair shorter than standing.
rc = sheet.crop((man["frames"]["idle"]*cellW, 0, (man["frames"]["idle"]+1)*cellW, cellH))
bb = rc.getbbox(); target_h = int((bb[3]-bb[1]) * 0.94 * float(__import__("os").environ.get("SCALE_MUL", 1)))   # SCALE_MUL: raised-arm windows shrink the body — compensate per set
s = min(target_h / cells[0].height, (cellW-2) / cells[0].width)
cells = [c.resize((max(1, round(c.width*s)), max(1, round(c.height*s))), Image.LANCZOS) for c in cells]

need = sum(1 for cn in cellnames if cn not in man["frames"])
out = Image.new("RGBA", (cellW*(man["cols"]+need), cellH), (0,0,0,0))
out.paste(sheet, (0, 0))
nxt = man["cols"]
for cn, c in zip(cellnames, cells):
    col = man["frames"].get(cn)
    if col is None:
        col = nxt; nxt += 1; man["frames"][cn] = col
    out.paste(Image.new("RGBA", (cellW, cellH), (0,0,0,0)), (col*cellW, 0))
    out.paste(c, (col*cellW + (cellW-c.width)//2, cellH - pad - c.height), c)
man["cols"] = nxt
out.save(adir / f"{name}.png", optimize=True)
(adir / f"{name}.json").write_text(json.dumps(man))
print(f"{name}: packed {dict(zip(cellnames, picks))}, cols {man['cols']}, scale {s:.3f}")
