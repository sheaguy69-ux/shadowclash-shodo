#!/usr/bin/env python3
"""pack_shodo_air.py — foot-anchored per-cell packer for AERIAL boards.

Run/grounded rows use pack_shodo_row.py (one union window, one scale — the stride
bob is real). AERIAL rows (jump/fall/air/wall) must NOT: the union window of a jump
arc spans ground contact AND apex, so a shared scale crushes the body. Per the house
rule (SHEET_V 215): the engine already lifts the sprite by world height, so a cell
that also carries the jump's altitude double-counts it — aerial cells are foot-anchored
at footY, never carrying their own lift.

Each of the 8 frames: white-composite, key to alpha, crop to ITS OWN ink bbox, scale
to the idle-anchored FIGURE height, paste bottom-anchored at footY (or at a per-cell
offset from BEATS/FOOTY_OFFSETS). MIRROR=1 flips to LEFT-facing.

    BEATS="1 2 3 4 6 7"         pick frames (default 1..8)
    FOOTY_OFFSETS="0 0 -40 -80 ..."  per-cell vertical lift (px UP, applied in-cell;
        default 0 = feet at footY). Pass positive = higher.
"""
import sys, os, json, pathlib, glob
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
SP = REPO / 'web' / 'assets' / 'sprites'
name = sys.argv[1]
fdir = sys.argv[2]
keys = sys.argv[3:]
assert 1 <= len(keys) <= 8
beats = [int(x) for x in os.environ.get('BEATS', '1 2 3 4 5 6 7 8').split()][:8]
offsets = [int(x) for x in os.environ.get('FOOTY_OFFSETS', '0 0 0 0 0 0 0 0').split()][:8]
offsets += [0] * (8 - len(offsets))
stage = os.environ.get('STAGE', keys[0] + '_stg')

man = json.loads((SP / f'{name}.json').read_text())
sheet = Image.open(SP / f'{name}.png').convert('RGBA')
cellW, cellH, pad = man['frameW'], man['frameH'], man['frameH'] - man['footY']

def key_frame(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    a = np.array(Image.alpha_composite(bg, im).convert('RGB'))
    ink = a.min(2) < 130
    ys, xs = np.where(ink)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    crop = a[y0:y1+1, x0:x1+1].copy()
    bgcand = crop.min(2) >= 205
    lbl, n = ndimage.label(bgcand)
    border = np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))
    bgmask = np.isin(lbl, border[border != 0])
    alpha = np.where(bgmask, 0, 255).astype(np.uint8)
    encl = bgcand & ~bgmask
    elbl, en = ndimage.label(encl)
    for k in range(1, en + 1):
        m = elbl == k
        if m.sum() < 15: continue
        ring = ndimage.binary_dilation(m, iterations=4) & ~bgcand
        if ring.sum() < 8: continue
        ringpx = crop[ring].astype(int)
        neutral = (ringpx.max(1) - ringpx.min(1)).mean() < 22
        if ringpx.mean() < 60 and neutral and m.sum() < 2600: continue
        crop[m] = np.median(ringpx, axis=0).astype(np.uint8)
    # torso height = ink above the bottom 25% (extended legs excluded) — the BODY
    torso = int((ys[ys < ys.max() - (ys.max()-ys.min())*0.25].max()) - ys.min()) if len(ys) else 0
    return Image.fromarray(np.dstack([crop, alpha])), int(y1 - y0), torso  # img, fig h, torso h

raws = [Image.open(pathlib.Path(fdir) / f'frame-{b:02d}.png') for b in beats]
if os.environ.get('MIRROR'):
    raws = [ImageOps.mirror(im) for im in raws]
keyed = [key_frame(im) for im in raws]

# idle-anchored figure scale: body must not shrink vs standing (never-shrink law).
# ONE shared scale for the whole row, anchored on the MEDIAN TORSO height (ink above the
# bottom quarter — extended legs are pose, the torso is the body).
rc = sheet.crop((man['frames']['idle']*cellW, 0, (man['frames']['idle']+1)*cellW, cellH))
bb = rc.getbbox()
idle_h = (bb[3]-bb[1]) if bb else cellH - pad - 20
torsos = sorted(t for _, _, t in keyed)
median_torso = torsos[len(torsos)//2]
s = min(idle_h * 0.96 / median_torso, (cellW - 2) / max((img.width for img, _, _ in keyed)))
print('median torso', median_torso, 'scale', round(s, 3))

cells = []
for img, fh, _ in keyed:
    w = max(1, round(img.width * s)); h = max(1, round(img.height * s))
    cells.append(img.resize((w, h), Image.LANCZOS))

before = np.array(sheet.convert('RGBA'))
out = Image.new('RGBA', (cellW*(man['cols']+8), cellH), (0, 0, 0, 0))
out.paste(sheet, (0, 0))
nxt = man['cols']
staging = []
for i, c in enumerate(cells, 1):
    col = nxt; nxt += 1
    staging.append(col)
    man['frames'][f'{stage}{i}'] = col
    out.paste(Image.new('RGBA', (cellW, cellH), (0, 0, 0, 0)), (col*cellW, 0))
    lift = offsets[i-1]
    y = cellH - pad - c.height - lift
    out.paste(c, (col*cellW + (cellW - c.width)//2, y), c)
man['cols'] = nxt

for i, k in enumerate(keys, 1):
    man['frames'][k] = staging[i-1]
for i in range(1, 9):
    man['frames'].pop(f'{stage}{i}', None)

out.save(SP / f'{name}.png', optimize=True)
(SP / f'{name}.json').write_text(json.dumps(man))

after = np.array(out.convert('RGBA'))
oldcols = man['cols'] - 8
reg = slice(0, oldcols*cellW)
d = (before[:, reg] != after[:, reg]).any(axis=2)
vis = before[:, reg, 3] >= 8
diff = int(d.sum()); vdiff = int((d & vis).sum())
print(f'{name} {keys[0]}..{keys[-1]} cells {staging[0]}-{staging[-1]} scale {s:.3f} cols {man["cols"]} '
      f'{"OK" if diff==0 else "BYTE-DIFF"} (diff {diff}, visible {vdiff})')
sys.exit(0 if diff == 0 else 1)
