#!/usr/bin/env python3
"""Roster head/body-cut scanner — the check that found Shin's sheared jump hoods (606)
and Ember's wall-eaten wallslide bodies (607).

For every cell of every fighter json in web/assets/sprites/: flags
  - ink touching the frame's top edge (rows 0-2)  -> something got clipped at pack
  - a flat plateau at ink-top (>=30% of columns sharing the top row)
    -> the straight-cut signature of a cropped head
Every flag needs EYES before action: raised blades, horizontal scarves/dives,
halo discs and smoke forms all flag legitimately (see SHEET_V 606 entry).
Exit 0 with a report; exit 1 only if a cell touches the top edge (hard clip).

ponytail: single alpha>=8 estimator; the two-estimator FX-masked pass (595) is
the upgrade path when a flag needs confirming.
"""
import json, glob, sys
from PIL import Image
import numpy as np

# Eyes-cleared flags (Aug 23 2026, SHEET_V 606/607): pose ink or sub-visible tip
# clips, NOT head cuts. A flag listed here never fails the check; anything new does.
CLEARED = {
    'executioner': {'xsuso6'},          # super's spark burst touches frame top
    'kael': {'kfang4','aup5','xcuph5'}, # launcher trail tip at edge; raised blades
    'mizu': {'hup5'},                   # vertical staff tip at frame top
    'exile': {'light2','xairb'},        # mist form; aerial trail arc
    'mokurai': {'hhalo2'},              # drawn halo disc
    'oni': {'afwd4','afwd5','hneu6'},   # benched; FX arcs
    'shin': {'sup3','sup5','roll_6','jump2','ajump3','ajump4','wire3','wire5'},
}

hard = 0
for jp in sorted(glob.glob('web/assets/sprites/*.json')):
    name = jp.split('/')[-1][:-5]
    try:
        d = json.load(open(jp))
        if 'frames' not in d or 'frameW' not in d: continue
        A = np.array(Image.open(jp[:-5]+'.png').convert('RGBA'))[:,:,3]
    except Exception as e:
        print(f'{name}: skip ({e})'); continue
    fw, fh = d['frameW'], d['frameH']
    seen, flags = set(), []
    for k, idx in sorted(d['frames'].items(), key=lambda kv: kv[1]):
        if not isinstance(idx, int) or idx in seen: continue
        seen.add(idx)
        if (idx+1)*fw > A.shape[1]: continue
        m = A[:, idx*fw:(idx+1)*fw] >= 8
        ys = np.where(m.any(axis=1))[0]
        if not len(ys): continue
        top = ys[0]
        cols = np.where(m.any(axis=0))[0]
        if len(cols) < 20: continue
        coltop = np.array([np.argmax(m[:, x]) for x in cols])
        frac = (coltop <= top+1).sum() / len(cols)
        cleared = k in CLEARED.get(name, ())
        if top <= 2:
            flags.append((k, int(top), round(float(frac), 2), 'EDGE' + (' (cleared)' if cleared else '')))
            if not cleared: hard += 1
        elif frac > 0.30 and (coltop <= top+1).sum() > 35:
            flags.append((k, int(top), round(float(frac), 2), 'flat-top' + (' (cleared)' if cleared else '')))
    status = 'CLEAN' if not flags else f'{len(flags)} flags'
    print(f'{name}: {len(seen)} cells, {status}')
    for f in flags: print('   ', f)
sys.exit(1 if hard else 0)
