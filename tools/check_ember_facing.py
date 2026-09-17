#!/usr/bin/env python3
"""Every Ember cell drawn facing RIGHT must carry its `mirror` flag.

The roster is authored FACING LEFT and the engine mirrors toward the opponent, so a cell
drawn facing RIGHT plays backwards for its whole move. `mirror` in the manifest flips those
cells back at draw time — a render flag, not an art edit, so the sheet stays append-only.

WHY THIS EXISTS — owner, Sep 16 2026: "when I run with him, he run backwards ... every time
he jump, he only turned one way". Both were the same thing: his run board (416-423) and his
jump board (432-439) were packed mirrored and never flagged. Fifty cells were in that state,
and three of them (441, 487, 488) were MY doing — 834 appended repaired medium cells and
repointed the keys without carrying the flag off the originals. Any pass that re-packs a
flagged cell has to carry its flag, and nothing was checking.

THE RULER is his one ivory teardrop eye inside a dark hood: score = (eye_x -
head_centroid_x) / head_width over the top of the ink. It passes 14/14 known answers, but it
is NOISY below |0.20| — a head pitched forward puts the eye right of its own centroid on a
left-facing cell (erake4/5 read +0.19/+0.14 and are canon on inspection). So the verdict is
taken on the ROW MEDIAN, never on one beat.

    python3 tools/check_ember_facing.py
"""
import json, pathlib, re, sys
from collections import defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'sprites'))
from keyer_emu import keyed_cell  # noqa: E402

MIRRORED_ROW = 0.12     # a row this positive is drawn facing right
CANON_ROW = -0.006      # a row this negative is canon; its odd beats are detector noise


def eye_offset(a):
    m = a[:, :, 3] >= 8
    if m.sum() < 300: return None
    ys, xs = np.where(m)
    y0, y1 = ys.min(), ys.max()
    bright = (a[:, :, :3].min(2) >= 195) & m
    for frac in (0.45, 0.60, 0.75):
        head = m.copy(); head[y0 + int((y1 - y0) * frac):] = False
        hy, hx = np.where(head)
        if len(hx) < 50: continue
        hc, hw = hx.mean(), hx.max() - hx.min() + 1
        lab, n = ndimage.label(bright & head)
        best = None
        for i in range(1, n + 1):
            b = lab == i; s = int(b.sum())
            if not (25 <= s <= 450): continue
            yy, xx = np.where(b)
            if s / ((yy.max() - yy.min() + 1) * (xx.max() - xx.min() + 1)) < 0.40: continue
            if best is None or s > best[0]: best = (s, xx.mean())
        if best: return (best[1] - hc) / hw
    return None


def main():
    sp = ROOT / 'web' / 'assets' / 'sprites'
    man = json.loads((sp / 'ember.json').read_text())
    W = man['frameW']
    sheet = np.array(Image.open(sp / 'ember.png').convert('RGBA'))
    F = {k: v for k, v in man['frames'].items() if isinstance(v, int)}
    flags = {int(k) for k, v in man.get('mirror', {}).items() if v}

    score = {}
    for c in sorted(set(F.values())):
        score[c] = eye_offset(keyed_cell(sheet[:, c * W:(c + 1) * W]))

    rows, owner = defaultdict(set), defaultdict(set)
    for k, v in F.items():
        m = re.match(r'^(.*?)(\d+)$', k)
        name = m.group(1) if m else k
        rows[name].add(v); owner[v].add(name)
    med = {n: (float(np.median([score[c] for c in cs if score[c] is not None]))
               if any(score[c] is not None for c in cs) else None)
           for n, cs in rows.items()}
    mrows = {n for n, v in med.items() if v is not None and v >= MIRRORED_ROW}
    crows = {n for n, v in med.items() if v is not None and v <= CANON_ROW}

    want = {c for n in mrows for c in rows[n] if not (owner[c] & crows)}
    missing = sorted(want - flags)
    stale = sorted((flags & set(F.values())) - want)

    print(f'  {len(mrows)} rows drawn facing right: {" ".join(sorted(mrows))}')
    print(f'  {len(want)} cells need the flag, {len(flags)} carry it')
    bad = False
    if missing:
        bad = True
        for c in missing:
            print(f'  FAIL cell {c} is drawn facing right and has NO mirror flag — '
                  f'{",".join(sorted(k for k, v in F.items() if v == c))} plays backwards')
    if stale:
        bad = True
        for c in stale:
            print(f'  FAIL cell {c} carries a mirror flag but its row reads canon — '
                  f'the flag turns it backwards')
    if bad: sys.exit(1)
    print('  facing flags OK')


if __name__ == '__main__':
    main()
