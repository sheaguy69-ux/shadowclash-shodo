"""Roster-wide sweep for HARD VERTICAL CUT-OFFS on cells the engine actually draws.

Owner law: an effect that ends in a straight cut is deleted entirely, never faded, and the
body is never touched. This SHORTLISTS candidates — a blade edge and the drawn wall stroke
are legitimately straight, so every hit needs a human look before anything is removed.

A hit is a column with >=MIN px of ink whose run is >=85% solid and whose neighbouring
column is empty across that same span. Measured POST-KEYER, because the engine keys at
draw time and file alpha lies.

    python3 tools/sprites/session-2026-09-02/straight_cut_sweep.py            # all nine
    python3 tools/sprites/session-2026-09-02/straight_cut_sweep.py exile oni  # some
"""
import json, sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from keyer_emu import keyed_cell
Image.MAX_IMAGE_PIXELS = None
R = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'web', 'assets', 'sprites')
R = os.path.normpath(R)
MIN = 20
ALL = ['executioner', 'mizu', 'shin', 'tsubasa', 'kael', 'mokurai', 'exile', 'oni', 'ember']

def sweep(name):
    m = json.load(open(f'{R}/{name}.json'))
    fw = m['frameW']
    sheet = np.array(Image.open(f'{R}/{name}.png').convert('RGBA'))
    live = {}
    for k, c in m['frames'].items(): live.setdefault(c, []).append(k)
    hits = []
    for c in sorted(live):
        a = keyed_cell(sheet[:, c*fw:(c+1)*fw])[..., 3] > 40
        if not a.any(): continue
        cols = a.sum(0)
        for x in range(fw - 1):
            if cols[x] < MIN: continue
            ys = np.nonzero(a[:, x])[0]
            run = int(ys.max() - ys.min() + 1)
            if run < MIN or cols[x] < run * 0.85: continue
            if a[ys.min():ys.max()+1, x+1].sum() == 0: hits.append((c, live[c], x, run, 'right'))
            elif x and a[ys.min():ys.max()+1, x-1].sum() == 0: hits.append((c, live[c], x, run, 'left'))
    return hits

if __name__ == '__main__':
    names = sys.argv[1:] or ALL
    total = 0
    for n in names:
        h = sweep(n)
        total += len(h)
        print(f'{n}: {len(h)} straight vertical edges >= {MIN}px on live cells')
        for c, keys, x, run, side in sorted(h, key=lambda t: -t[3])[:8]:
            print(f'    cell {c:4d}  {",".join(keys)[:30]:30s}  x={x:3d} run={run:3d} ({side} empty)')
    print(f'\nTOTAL {total}. A blade edge and the drawn wall stroke are legitimately straight — LOOK before deleting.')
