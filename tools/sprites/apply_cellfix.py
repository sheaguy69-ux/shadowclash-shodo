#!/usr/bin/env python3
"""Write per-cell RENDER corrections into a sheet manifest. No art bytes move.

Two defects, two maps, both keyed by cell index and both applied by drawSprite:

  footAdj[idx] = footY - (lowest opaque row)   how many SHEET px the pose was
      packed short of the floor. The engine subtracts it, so the pose lands on
      the floor line. Cells within TOL are skipped — a 1-2px packing margin is
      under one screen pixel, and "correcting" it is noise.

  mirror[idx] = 1                              the cell was packed FACING RIGHT.
      Every sheet is authored facing LEFT and the engine mirrors toward the
      opponent, so such a cell plays turned AWAY for the whole move. The engine
      flips it back.

Sheets stay append-only either way: this is data, not pixels.

Usage: apply_cellfix.py <fighter> --foot   <idx> [<idx> ...]
       apply_cellfix.py <fighter> --mirror <idx> [<idx> ...]
       apply_cellfix.py <fighter> --clear
"""
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SPR = os.path.join(ROOT, 'web', 'assets', 'sprites')
ALPHA, MIN_RUN, TOL = 32, 3, 2


def lowest_row(sheet, idx, fw, fh):
    px = sheet.crop((idx * fw, 0, (idx + 1) * fw, fh)).load()
    for y in range(fh - 1, -1, -1):
        if sum(1 for x in range(fw) if px[x, y][3] >= ALPHA) >= MIN_RUN:
            return y
    return None


def write(path, man, ind):
    with open(path, 'w') as fh:
        json.dump(man, fh, indent=ind)
        fh.write('\n')          # keep the trailing newline the manifests ship with


def indent_of(path):
    """Match the file's existing indentation — rewriting it churns the whole
    manifest into the diff and buries the two lines that actually changed."""
    for line in open(path):
        m = re.match(r'^( +)"', line)
        if m:
            return len(m.group(1))
    return 2


def main():
    name = sys.argv[1]
    jf = os.path.join(SPR, f'{name}.json')
    man = json.load(open(jf))
    IND = indent_of(jf)
    if '--clear' in sys.argv:
        man.pop('footAdj', None)
        man.pop('mirror', None)
        write(jf, man, IND)
        print('cleared footAdj + mirror on', name)
        return

    idxs = [int(a) for a in sys.argv[2:] if not a.startswith('--')]

    if '--mirror' in sys.argv:
        mir = dict(man.get('mirror', {}))
        for idx in idxs:
            mir[str(idx)] = 1
        man['mirror'] = {k: mir[k] for k in sorted(mir, key=int)}
        write(jf, man, IND)
        print(f'{name}: mirror now holds {len(man["mirror"])} cells -> {sorted(map(int, man["mirror"]))}')
        return

    sheet = Image.open(os.path.join(SPR, f'{name}.png')).convert('RGBA')
    fw, fh, footY, scale = man['frameW'], man['frameH'], man['footY'], man['scale']
    adj = dict(man.get('footAdj', {}))
    for idx in idxs:
        low = lowest_row(sheet, idx, fw, fh)
        if low is None:
            print(f'  [{idx}] EMPTY — skipped')
            continue
        gap = footY - low
        if gap <= TOL:
            print(f'  [{idx}] gap {gap}px <= tol — skipped')
            continue
        adj[str(idx)] = gap
        print(f'  [{idx}] gap {gap} sheet px = {gap * scale:.2f} screen px -> planted')
    man['footAdj'] = {k: adj[k] for k in sorted(adj, key=int)}
    write(jf, man, IND)
    print(f'{name}: footAdj now holds {len(man["footAdj"])} cells')


if __name__ == '__main__':
    main()
