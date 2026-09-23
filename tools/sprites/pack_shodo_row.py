#!/usr/bin/env python3
"""pack_shodo_row.py — ONE command per approved board row.

Packs an 8-frame approved Shodo board into a fighter sheet, append-only:

    python3 tools/sprites/pack_shodo_row.py <fighter> <board_dir> <key1> [key2 ...]

The board's frame-01..08.png are white-composited (cards are RGBA black-underlay),
packed under a staging prefix with ONE idle-anchored scale (pack_i2v8 rules),
appended at the sheet tail, then the target keys are repointed to the new cells
in order (key1<-beat1, key2<-beat2, ...). Extra beats beyond the keys stay packed
but unreferenced (strip candidates). Originals asserted byte-identical.

Env: BEATS="1 2 3 4 6 7" to pick specific frames (default 1..8).
     STAGE=name to set the staging prefix (default derived from first key).
     TARGET_H=pixels to bootstrap a clean atlas without an old idle cell.
     TARGET_BEAT=1..8 selects which authored beat owns TARGET_H (default 1).
"""
import sys, os, json, pathlib, glob, subprocess, hashlib
import numpy as np
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None   # executioner's strip passed PIL's 179M-pixel bomb cap at 601 cols (SHEET_V 863)

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
SP = REPO / 'web' / 'assets' / 'sprites'
name = sys.argv[1]
fdir = sys.argv[2]
keys = sys.argv[3:]
assert 1 <= len(keys) <= 16, '1..16 target keys'
beats = [int(x) for x in os.environ.get('BEATS', '1 2 3 4 5 6 7 8').split()][:16]
# ⛔ A ROW IS NOT ALWAYS EIGHT BEATS. The chudan set the owner commissioned ships a
# TWO-card stance idle and seven SIX-card rows, and the old `== 8` assert made the only
# way to pack them padding each row out with repeats — which appends dead cells nobody
# references, exactly the orphan debris the sheet is supposed to stay clear of. The
# beat count now simply follows BEATS, and the append below reserves what it actually
# writes. Default is still 1..8, so every existing call behaves identically.
assert 1 <= len(beats) <= 16, 'BEATS must name 1..16 frames'
assert len(keys) <= len(beats), 'more target keys than beats'
stage = os.environ.get('STAGE', keys[0] + '_stg')

man = json.loads((SP / f'{name}.json').read_text())
sheet = Image.open(SP / f'{name}.png').convert('RGBA')
cellW, cellH, pad = man['frameW'], man['frameH'], man['frameH'] - man['footY']

# 1. white-composite the RGBA cards (pack_i2v8 needs light-bg RGB ink detection)
raws = []
for b in beats:
    im = Image.open(pathlib.Path(fdir) / f'frame-{b:02d}.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    raws.append(Image.alpha_composite(bg, im).convert('RGB'))

# 2. shared window = union ink bbox (ink = min(RGB) < 130, packer's own rule)
x0, y0, x1, y1 = 10**9, 10**9, 0, 0
for im in raws:
    a = np.array(im)
    ys, xs = np.where(a.min(2) < 130)
    x0, y0 = min(x0, xs.min()), min(y0, ys.min())
    x1, y1 = max(x1, xs.max()), max(y1, ys.max())
# ⛔ CLAMP TO THE CARD. PIL pads a crop that runs past the edge with BLACK, and a
# black strip on the crop border cuts the page off from the border flood below — the
# whole page then reads as an enclosed pocket and gets repainted solid. Every one of
# the executioner ceremony cards draws to the right edge, so all four rows packed as
# a figure sitting on a brown slab until this line existed.
iw, ih = raws[0].size
x0, y0, x1, y1 = max(0, x0-6), max(0, y0-6), min(iw, x1+6), min(ih, y1+6)

# 3. alpha from border-connected white; keep enclosed white (glowing eyes)
from scipy import ndimage
cells = []
for im in raws:
    a = np.array(im.crop((x0, y0, x1, y1)))
    bgcand = a.min(2) >= 205
    lbl, n = ndimage.label(bgcand)
    border = np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))
    bg = np.isin(lbl, border[border != 0])
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    encl = bgcand & ~bg
    # POCKETS=drop: every enclosed page region is NEGATIVE SPACE, cut it out. The
    # default below keeps a pocket opaque so a white-drawn eye survives; a fighter
    # whose eyes are painted in ink (the executioner's are yellow) has no such pocket
    # to protect, and the default instead paints a slab of page between his legs.
    if os.environ.get('POCKETS') == 'drop':
        alpha[encl] = 0
        encl = np.zeros_like(encl)
        # ⛔ AND THEN DE-HALO. A binary key keeps the ink/page BLEND pixels at full
        # opacity, and cutting a pocket open exposes a fresh interior edge made of
        # them — measured 4-8% page-bright rim against 0.01-2.5% on every row already
        # shipped on this sheet, which on the ash stage is a lit outline traced round
        # the figure. Only page-bright pixels ALREADY TOUCHING transparency go, twice,
        # so this erases negative space and can never reach ink: the eyes are yellow,
        # min-channel far below 190, and enclosed by hood ink besides.
        page = a.min(2) >= 190
        for _ in range(2):
            open_edge = ndimage.binary_dilation(alpha == 0) & page & (alpha > 0)
            if not open_edge.any(): break
            alpha[open_edge] = 0
    elbl, en = ndimage.label(encl)
    for k in range(1, en + 1):
        m = elbl == k
        if m.sum() < 15: continue
        ring = ndimage.binary_dilation(m, iterations=4) & ~bgcand
        if ring.sum() < 8: continue
        ringpx = a[ring].astype(int)
        neutral = (ringpx.max(1) - ringpx.min(1)).mean() < 22
        if ringpx.mean() < 60 and neutral and m.sum() < 2600: continue
        a[m] = np.median(ringpx, axis=0).astype(np.uint8)
    h = a.shape[0]
    band = slice(int(h*0.62), h)
    gray = (a[band].min(2) > 95) & (a[band].max(2).astype(int) - a[band].min(2) < 44)
    alpha[band][gray] = 0
    alpha[:, :4] = 0; alpha[:, -4:] = 0; alpha[:4] = 0; alpha[-4:] = 0
    cells.append(Image.fromarray(np.dstack([a, alpha])))

# 4. one idle-anchored scale (never-shrink law)
# SCALE=0.75 overrides the idle anchor for intentionally-compressed rows
# (dodge rolls, crouches) that must read LOW against the standing figure.
if os.environ.get('TARGET_H'):
    target_h = float(os.environ['TARGET_H'])
    target_beat = int(os.environ.get('TARGET_BEAT', '1'))
    assert 1 <= target_beat <= 8, 'TARGET_BEAT must be 1..8'
    bb = cells[target_beat - 1].getchannel('A').getbbox()
    assert bb, 'target Shodo beat is blank'
    source_h = bb[3] - bb[1]
else:
    rc = sheet.crop((man['frames']['idle']*cellW, 0, (man['frames']['idle']+1)*cellW, cellH))
    bb = rc.getbbox(); target_h = int((bb[3]-bb[1]) * 0.94) if bb else cellH - pad - 20
    source_h = cells[0].height
if os.environ.get('SCALE'):
    s = float(os.environ['SCALE'])
else:
    s = min(target_h / source_h, (cellW-2) / cells[0].width)
cells = [c.resize((max(1, round(c.width*s)), max(1, round(c.height*s))), Image.LANCZOS) for c in cells]

# 5. append-only: originals byte-identical, staging cells appended at tail
before = np.array(sheet.convert('RGBA'))
need = len(cells)          # reserve what is actually written, not a fixed eight
out = Image.new('RGBA', (cellW*(man['cols']+need), cellH), (0, 0, 0, 0))
out.paste(sheet, (0, 0))
nxt = man['cols']
staging = []
for i, c in enumerate(cells, 1):
    col = nxt; nxt += 1
    staging.append(col)
    man['frames'][f'{stage}{i}'] = col
    out.paste(Image.new('RGBA', (cellW, cellH), (0, 0, 0, 0)), (col*cellW, 0))
    bb = c.getchannel('A').getbbox()
    assert bb, f'beat {i} is blank'
    out.paste(c, (col*cellW + (cellW-c.width)//2, man['footY'] - bb[3]), c)
man['cols'] = nxt

# 6. repoint target keys, drop staging
for i, k in enumerate(keys, 1):
    man['frames'][k] = staging[i-1]
for i in range(1, len(cells) + 1):
    man['frames'].pop(f'{stage}{i}', None)

out.save(SP / f'{name}.png', optimize=True)
(SP / f'{name}.json').write_text(json.dumps(man))

# 7. byte-identity: original region (before cols) must be pixel-identical
after = np.array(out.convert('RGBA'))
oldcols = man['cols'] - len(cells)
reg = slice(0, oldcols*cellW)
d = (before[:, reg] != after[:, reg]).any(axis=2)
vis = before[:, reg, 3] >= 8
diff = int(d.sum()); vdiff = int((d & vis).sum())
status = 'OK' if diff == 0 else 'BYTE-DIFF'
print(f'{name} {keys[0]}..{keys[-1]} cells {staging[0]}-{staging[-1]} scale {s:.3f} cols {man["cols"]} {status} (diff px {diff}, visible {vdiff})')
sys.exit(0 if diff == 0 else 1)
