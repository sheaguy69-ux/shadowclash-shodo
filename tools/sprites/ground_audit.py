#!/usr/bin/env python3
"""Measure every packed cell's foot line against the sheet's footY.

The engine anchors a cell so that its row `footY` lands exactly on the
player's bottom edge (drawSprite: translate(y + height) then drawImage at
-footY*S).  So a cell whose lowest opaque pixel sits ABOVE footY renders
FLOATING by (footY - bottom) * scale screen pixels, and one below footY
sinks into the floor.

Usage:  python3 tools/sprites/ground_audit.py [fighter ...]
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SPR = os.path.join(ROOT, 'web', 'assets', 'sprites')
ALPHA = 32          # a pixel counts as "body" at/above this alpha
MIN_RUN = 3         # ...and only if >= this many such pixels share the row
                    # (kills stray keyed specks / drop-shadow crumbs)


def cell_metrics(sheet, idx, fw, fh):
    """Per-COLUMN metrics for cell idx (docs/FLOOR-AUDIT-2026-07-25.md method).

    A whole-cell "lowest ink" check misses the real bug: a kneel can read
    +1px while the body hovers 38px, held up by a prop. So we also measure the
    middle 40% of the figure (bodyLow) and how much of the silhouette actually
    reaches the contact line (support%).
    """
    px = sheet.crop((idx * fw, 0, (idx + 1) * fw, fh)).load()
    top = bottom = left = right = None
    colLow = {}
    for y in range(fh):
        run = [x for x in range(fw) if px[x, y][3] >= ALPHA]
        if len(run) < MIN_RUN:
            continue
        if top is None:
            top = y
        bottom = y
        lo, hi = run[0], run[-1]
        left = lo if left is None else min(left, lo)
        right = hi if right is None else max(right, hi)
        for x in run:
            colLow[x] = y
    if top is None:
        return None
    # middle 40% of the occupied width = torso/legs, not an outstretched weapon
    span = right - left + 1
    m0, m1 = left + span * 0.3, left + span * 0.7
    mid = [v for x, v in colLow.items() if m0 <= x <= m1]
    bodyLow = max(mid) if mid else bottom
    support = round(100.0 * sum(1 for v in colLow.values()
                                if v >= bottom - 3) / len(colLow), 1)
    return top, bottom, left, right, bodyLow, support


def audit(name):
    man = json.load(open(os.path.join(SPR, f'{name}.json')))
    sheet = Image.open(os.path.join(SPR, f'{name}.png')).convert('RGBA')
    fw, fh, footY, scale = man['frameW'], man['frameH'], man['footY'], man['scale']
    cols = man.get('cols', sheet.width // fw)
    names = {}
    for k, v in man.get('frames', {}).items():
        names.setdefault(v, []).append(k)
    out = []
    for i in range(cols):
        m = cell_metrics(sheet, i, fw, fh)
        if m is None:
            out.append(dict(idx=i, names=sorted(names.get(i, [])), empty=True))
            continue
        top, bottom, left, right, bodyLow, support = m
        out.append(dict(idx=i, names=sorted(names.get(i, [])), empty=False,
                        top=top, bottom=bottom, left=left, right=right,
                        gap=footY - bottom,                    # +ve = floats
                        screen=round((footY - bottom) * scale, 2),
                        bodyGap=footY - bodyLow,               # ignores weapons
                        bodyScreen=round((footY - bodyLow) * scale, 2),
                        support=support,
                        h=bottom - top + 1))
    return man, out


def main():
    fighters = sys.argv[1:] or sorted(
        f[:-5] for f in os.listdir(SPR) if f.endswith('.json'))
    report = {}
    for f in fighters:
        man, cells = audit(f)
        report[f] = dict(frameW=man['frameW'], frameH=man['frameH'],
                         footY=man['footY'], scale=man['scale'],
                         cols=man.get('cols'), cells=cells)
    json.dump(report, sys.stdout)


if __name__ == '__main__':
    main()
