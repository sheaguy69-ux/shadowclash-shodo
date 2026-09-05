#!/usr/bin/env python3
"""Port a packed row from one tree's sheet onto another's, append-only.

    python3 tools/sprites/port_row.py <fighter> <row> [<row> ...] [--scale 0.72] [--dry]
    (source tree defaults to $PORT_SRC or ~/SHADOWCLASH-RECOVERED)

WHY THIS EXISTS. Twelve of the twenty-two DIR_MOVES art rows are absent from the SHODO
sheets and every one of them is packed on SHADOWCLASH-RECOVERED: the sheets were rebuilt
and the directional rows never came across. So this is a PORT of art that is already
drawn and already approved — not a generation, and not a substitution.

⛔ RAW PIXELS, NEVER KEYED. The engine keys at DRAW time (keyedShodoCell), so a cell that
is keyed on the way in gets keyed twice and loses its rim. Cells are copied byte-for-byte
out of the source sheet.

⛔ ONE SCALE PER ROW, AND ONLY WHEN THE RULERS AGREE. --scale resamples foot-anchored in
premultiplied alpha (a straight-alpha resize fringes every edge). Omit it and the cells
are copied verbatim, which is the right answer whenever the size rulers DISAGREE: √area,
bbox width and bbox height on the idle pose conflict for mizu/tsubasa/ember/oni (width is
contaminated by weapon angle, area by pose), and resampling on a guess throws away pixels
you cannot get back. Only shin's three measures agree (0.70-0.79), so only shin is scaled.

⛔ GROW THE CELL, NEVER SHRINK THE FIGHTER. If a ported pose is wider or taller than the
target cell box, this REFUSES rather than clamping — bump frameW/frameH and re-run.

Append-only: new cells go at the sheet tail, the pre-existing region is asserted
byte-identical, and the JSON keys are repointed last.
"""
import argparse, hashlib, json, os, pathlib, sys
import numpy as np
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[2]
DST = REPO / 'web' / 'assets' / 'sprites'
SRC = pathlib.Path(os.environ.get('PORT_SRC', pathlib.Path.home() / 'SHADOWCLASH-RECOVERED')) / 'web/assets/sprites'

ap = argparse.ArgumentParser()
ap.add_argument('fighter'); ap.add_argument('rows', nargs='+')
ap.add_argument('--scale', type=float, default=None)
ap.add_argument('--dry', action='store_true')
a = ap.parse_args()

sman = json.loads((SRC / f'{a.fighter}.json').read_text())
dman = json.loads((DST / f'{a.fighter}.json').read_text())
for k in ('frameW', 'frameH', 'footY'):
    if sman[k] != dman[k]:
        sys.exit(f'geometry differs on {k}: source {sman[k]} target {dman[k]} — port needs a re-anchor pass')
fw, fh, footY = dman['frameW'], dman['frameH'], dman['footY']

ssheet = Image.open(SRC / f'{a.fighter}.png').convert('RGBA')
dsheet = Image.open(DST / f'{a.fighter}.png').convert('RGBA')
before = np.array(dsheet).copy()
cols = dman['cols']

def foot_anchor(cell, scale):
    """Resample in premultiplied alpha, then sit the lowest ink back on footY."""
    arr = np.array(cell).astype(np.float64)
    arr[:, :, :3] *= arr[:, :, 3:4] / 255.0                      # -> premultiplied
    small = Image.fromarray(arr.astype(np.uint8), 'RGBA').resize(
        (max(1, round(fw * scale)), max(1, round(fh * scale))), Image.LANCZOS)
    s = np.array(small).astype(np.float64)
    al = np.clip(s[:, :, 3:4], 1e-6, None)
    s[:, :, :3] = np.clip(s[:, :, :3] * 255.0 / al, 0, 255)      # -> straight
    small = Image.fromarray(s.astype(np.uint8), 'RGBA')
    out = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
    m = np.array(small)[:, :, 3] > 16
    if not m.any():
        out.paste(small, ((fw - small.width) // 2, footY - small.height))
        return out
    ys, xs = np.where(m)
    ox = (fw - small.width) // 2 + (small.width // 2 - int((xs.min() + xs.max()) / 2))
    out.paste(small, (ox, footY - int(ys.max()) - 1))
    return out

added, repoint = [], {}
for row in a.rows:
    keys = [f'{row}{i}' for i in range(1, 25) if f'{row}{i}' in sman['frames']]
    if not keys: sys.exit(f'{a.fighter}: no row `{row}` on the source sheet')
    for k in keys:
        idx = sman['frames'][k]
        cell = ssheet.crop((idx * fw, 0, (idx + 1) * fw, fh))
        if a.scale: cell = foot_anchor(cell, a.scale)
        m = np.array(cell)[:, :, 3] > 16
        if m.any():
            ys, xs = np.where(m)
            if xs.min() < 0 or xs.max() >= fw or ys.max() >= fh:
                sys.exit(f'{k} overflows the {fw}x{fh} cell — GROW the cell, do not clamp')
        added.append(cell); repoint[k] = cols + len(added) - 1
    print(f'  {a.fighter:10s} {row:10s} {len(keys)} beats -> cells '
          f'{repoint[keys[0]]}..{repoint[keys[-1]]}' + (f'  x{a.scale}' if a.scale else '  verbatim'))

if a.dry: sys.exit(0)

wide = Image.new('RGBA', (dsheet.width + len(added) * fw, fh), (0, 0, 0, 0))
wide.paste(dsheet, (0, 0))
for i, c in enumerate(added): wide.paste(c, (dsheet.width + i * fw, 0))
after = np.array(wide)[:, :dsheet.width]
if not np.array_equal(before, after):
    sys.exit('REFUSED: the pre-existing region changed — nothing written')
wide.save(DST / f'{a.fighter}.png')
dman['cols'] = cols + len(added)
dman['frames'].update(repoint)
(DST / f'{a.fighter}.json').write_text(json.dumps(dman, indent=2) + '\n')
print(f'  {a.fighter}: +{len(added)} cells, cols {cols} -> {dman["cols"]}, '
      f'{len(repoint)} keys pointed, originals byte-identical')
