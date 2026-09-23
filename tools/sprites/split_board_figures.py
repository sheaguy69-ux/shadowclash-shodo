#!/usr/bin/env python3
"""Split an approved multi-drawing board into per-FIGURE rects without cutting art.

⛔ NEVER CUT ON A GUTTER. The Ember handoff pack blocks individual export on 8 of its
own boards because claw tips and motion streaks cross the reading-order separations;
a column cut severs them, which is the owner's standing "no straight cutoffs".

Method: label connected ink, separate BODIES (chunky: lots of ink AND a well-filled
bbox) from their own flying parts (thin: long, sparse, often detached). Each thin
component is handed to the nearest body and joins its rect. Figure rects therefore
OVERLAP where a claw reaches into the next drawing's column -- which is what keeps
the claw.

Validated by `--selftest` against the 9 boards the handoff pack already resolved rects
for: exact figure counts, zero art loss. Do not tune a constant without re-running it.
"""
import numpy as np
from scipy import ndimage

ALPHA = 12        # the runtime keyer's own ink threshold
BODY_INK = 0.15   # of the largest component's ink
BODY_FILL = 0.18  # ink / bbox area -- a body is solid, an arc is not


def _components(ink):
    # ⛔ NO SIZE FILTER. Dropping "dust" cost 41px of real drawn ink on retreat-heavy
    # (a 4x11 sliver at 0.82 fill is a claw tip, not speckle). Nothing needs a floor:
    # only CHUNKY components become bodies, so a speck can never be a phantom figure,
    # and every speck is handed to the nearest body instead of thrown away.
    lab, n = ndimage.label(ink)
    out = []
    for sl, i in zip(ndimage.find_objects(lab), range(1, n + 1)):
        m = lab[sl] == i
        area = int(m.sum())
        h, w = m.shape
        out.append({'x0': sl[1].start, 'x1': sl[1].stop, 'y0': sl[0].start,
                    'y1': sl[0].stop, 'ink': area, 'fill': area / float(h * w)})
    return out


def figures(rgba):
    a = np.asarray(rgba)
    ink = a[:, :, 3] >= ALPHA
    if not ink.any():
        return []
    comps = _components(ink)
    if not comps:
        return []
    top = max(c['ink'] for c in comps)
    bodies = [c for c in comps if c['ink'] >= BODY_INK * top and c['fill'] >= BODY_FILL]
    if not bodies:
        bodies = [max(comps, key=lambda c: c['ink'])]
    loose = [c for c in comps if c not in bodies]

    # A single component can hold TWO OR MORE touching bodies. Split it at its own
    # thinnest ink columns, never at a fixed gutter.
    # ⛔ IT MUST SPLIT INTO AS MANY PIECES AS THE ROW'S PITCH IMPLIES, NOT ALWAYS TWO.
    # crouch-angular-sandals-v3 welds the middle two of its bottom row; a single cut
    # left one box straddling two whole drawings and lost the 8th figure entirely.
    # And the pitch must be re-measured with welded bodies EXCLUDED, or a weld inflates
    # the very median used to detect it.
    widths = np.array([b['x1'] - b['x0'] for b in bodies], float)
    med = np.median(widths)
    lean = widths[widths <= med * 1.6]
    pitch = float(np.median(lean)) if lean.size else float(med)
    split = []
    for b in bodies:
        w = b['x1'] - b['x0']
        n_parts = int(round(w / pitch)) if pitch > 0 else 1
        if w > pitch * 1.6 and n_parts >= 2:
            col = ink[b['y0']:b['y1'], b['x0']:b['x1']].sum(0).astype(float)
            cuts = []
            for j in range(1, n_parts):
                centre = int(len(col) * j / n_parts)
                lo = max(1, centre - int(pitch * 0.3))
                hi = min(len(col) - 1, centre + int(pitch * 0.3))
                if hi > lo:
                    cuts.append(b['x0'] + lo + int(np.argmin(col[lo:hi])))
            edges = [b['x0']] + sorted(set(cuts)) + [b['x1']]
            for a0, a1 in zip(edges[:-1], edges[1:]):
                if a1 > a0:
                    split.append({**b, 'x0': a0, 'x1': a1, 'welded': True})
        else:
            split.append(b)
    bodies = split

    figs = [{'x0': b['x0'], 'x1': b['x1'], 'y0': b['y0'], 'y1': b['y1'],
             'ink': b['ink'], 'welded': b.get('welded', False), 'parts': 0} for b in bodies]
    for c in loose:
        cx, cy = (c['x0'] + c['x1']) / 2, (c['y0'] + c['y1']) / 2
        j = min(range(len(figs)), key=lambda i: (
            (cx - (figs[i]['x0'] + figs[i]['x1']) / 2) ** 2 +
            0.35 * (cy - (figs[i]['y0'] + figs[i]['y1']) / 2) ** 2))
        f = figs[j]
        f['x0'] = min(f['x0'], c['x0']); f['x1'] = max(f['x1'], c['x1'])
        f['y0'] = min(f['y0'], c['y0']); f['y1'] = max(f['y1'], c['y1'])
        f['ink'] += c['ink']; f['parts'] += 1

    # ⛔ ROWS CLUSTER ON CENTRES, NOT ON GAPS. Requiring a transparent band between rows
    # fails whenever a lower drawing reaches up past an upper one's feet -- on
    # ground-rip-contact-v2 the two rows interleave and reading order came out
    # column-major (1 top-left, 2 BOTTOM-left, 3 top-middle...), which would have fed the
    # engine the beats in the wrong order.
    figs.sort(key=lambda f: (f['y0'] + f['y1']) / 2)
    cy = [(f['y0'] + f['y1']) / 2 for f in figs]
    fh = np.median([f['y1'] - f['y0'] for f in figs])
    rows, cur = [], [figs[0]]
    for i in range(1, len(figs)):
        if cy[i] - cy[i - 1] > fh * 0.5:
            rows.append(cur); cur = [figs[i]]
        else:
            cur.append(figs[i])
    rows.append(cur)
    out = []
    for ri, row in enumerate(rows, 1):
        row.sort(key=lambda f: (f['x0'] + f['x1']) / 2)
        for ci, f in enumerate(row, 1):
            out.append({'row': ri, 'col': ci, 'ordinal': len(out) + 1,
                        'rect': [int(f['x0']), int(f['y0']), int(f['x1']), int(f['y1'])],
                        'ink': int(f['ink']), 'loose_parts': f['parts'], 'welded': f['welded']})
    return out


def selftest(pack):
    """Known answer: the boards the pack itself resolved rects for."""
    import json, os
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    L = json.load(open(os.path.join(pack, 'FRAME-CROP-LAYOUTS.json')))
    man = {s['sha256']: s for s in json.load(open(os.path.join(pack, 'MANIFEST.json')))['sheets']}
    bad = 0
    for s in L['sources']:
        if not s.get('individual_frame_export_allowed'):
            continue
        rec = man.get(s['source_sha256'])
        if not rec:
            continue
        im = Image.open(os.path.join(pack, rec['file'])).convert('RGBA')
        got = figures(im)
        want = [f['rect'] for f in s['frames']]
        A = np.asarray(im)[:, :, 3] >= ALPHA
        lost = 0
        for w in want:
            sub = A[w[1]:w[3], w[0]:w[2]]
            if not sub.any():
                continue
            cov = np.zeros_like(sub)
            for gf in got:
                r = gf['rect']
                x0, y0 = max(r[0], w[0]), max(r[1], w[1])
                x1, y1 = min(r[2], w[2]), min(r[3], w[3])
                if x1 > x0 and y1 > y0:
                    cov[y0 - w[1]:y1 - w[1], x0 - w[0]:x1 - w[0]] = True
            lost += int((sub & ~cov).sum())
        ok = len(got) == len(want) and lost == 0
        bad += not ok
        print(f"{s['family_label'][:30]:32} want {len(want):2} got {len(got):2}  lost {lost:5}px  {'OK' if ok else 'FAIL'}")
    print('PASS' if not bad else f'{bad} FAILED')
    return bad


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == '--selftest':
        sys.exit(1 if selftest(sys.argv[2]) else 0)
    print(__doc__)
