#!/usr/bin/env python3
"""Split a PANELLED delivery board into one cleaned strip per row, ready for pack_rows.

    python3 tools/sprites/cut_panels.py <board.png> <outdir>

Written after hand-rolling the same band+wall detection three times in one night (D-2339's
taijutsu grid, the first-form AIR board, the SRISAA/SPECIAL board). Each row comes out as
`row<N>.png` plus the exact `--cuts` string to feed pack_rows.

Three things this exists to get right, and the mistake each one is guarding:

  BANDS  — split rows by DARK ink only. A board whose panels are outlined boxes connects
           every row into one blob if you threshold on "not background", and the AIR board
           did exactly that: four rows came back as a single band 0-941.

  WALLS  — found PER ROW, not once for the board. The SRISAA row has 6 panels and the
           SPECIAL row below it has 7, so one shared grid is wrong for at least one of them.

  BORDERS— whiten a fixed band around each wall, and nothing else. Do NOT try to identify
           the border as a component: a hollow-rectangle test (big bbox, sparse fill) also
           matches a fighter mid-dive, and it erased the AJUMP dive frame outright, leaving
           the speed lines behind. Position is safe; shape is not.
"""
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
DARK = 170          # his body reads under this; FX, paper and panel strokes read over it


def bands(A):
    """Rows of the page that hold a figure. Dark ink only — see BANDS above."""
    m = A.max(2) < DARK
    on = m.sum(1) > m.shape[1] * 0.004
    out, s = [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append((s, i)); s = None
    if s is not None:
        out.append((s, len(on)))
    return [g for g in out if g[1] - g[0] > 100]


def walls(A, y0, y1):
    """Vertical panel strokes inside one band: columns inked down almost its whole height.

    ⛔ THEN SNAPPED TO A UNIFORM PITCH. A raw scan also catches a speed-line fan or a limb
    that happens to run the band's full height — it reported EIGHT panels on the AIR board's
    neutral-aerial row, which has five, and duplicate walls 7px apart on the row below. The
    panel grid is machine-drawn and therefore even, so the outer two walls plus a panel count
    reconstruct it exactly, and any candidate that does not sit on that grid was never a wall.
    """
    frac = (A[y0:y1].max(2) < 245).mean(0)
    xs = np.where(frac > 0.85)[0]
    raw, s, pv = [], None, None
    for x in xs:
        if s is None:
            s = x
        elif x - pv > 6:            # a rounded corner reads as two adjacent columns
            raw.append((s + pv) // 2); s = x
        pv = x
    if s is not None:
        raw.append((s + pv) // 2)
    raw = [w for i, w in enumerate(raw) if i == 0 or w - raw[i - 1] > 20]   # dedupe
    if len(raw) < 3:
        return raw
    span = raw[-1] - raw[0]
    gaps = np.diff(raw)
    pitch = float(np.median(gaps[gaps >= np.max(gaps) * 0.6]))   # ignore the spurious short ones
    n = max(1, int(round(span / pitch)))
    grid = [int(round(raw[0] + span * k / n)) for k in range(n + 1)]
    return grid


def clean(A, w):
    """Whiten a band around every wall and every full-width stroke. Position, never shape."""
    H, W, _ = A.shape
    out = A.copy()
    for x in w:
        out[:, max(0, x - 9):min(W, x + 10)] = 255
    # ⛔ A PANEL BORDER IS ONE CONTINUOUS, FLAT-COLOURED LINE ACROSS ONE PANEL.
    # Two wrong tests came before this one. Mere COVERAGE cut white bands through the fighters
    # on the taijutsu board, where six wide figures clear any sane threshold together. Then a
    # full-PAGE run-length test stopped cutting anything, because each panel is its own rounded
    # box and its stroke only ever spans that panel. So: measure the run inside each panel, and
    # require the stroke to be near-uniform in colour — a prone fighter can span his panel, but
    # he is not one flat grey.
    ink = A.max(2) < 215
    spans = [(w[k], w[k + 1]) for k in range(len(w) - 1)] or [(0, W)]
    for y in range(H):
        for x0, x1 in spans:
            row = ink[y, x0:x1]
            if not row.any():
                continue
            idx = np.flatnonzero(np.diff(np.r_[0, row.view(np.int8), 0]))
            runs = idx[1::2] - idx[::2]
            if runs.max() < (x1 - x0) * 0.85:
                continue
            j = int(np.argmax(runs))
            seg = A[y, x0 + idx[::2][j]:x0 + idx[1::2][j]]
            if seg.std(0).mean() < 26:                  # a flat stroke, not a drawing
                out[max(0, y - 3):min(H, y + 4), x0:x1] = 255
    # ⛔ AND THE PANEL NUMERAL GOES WITH IT. A board that prints "1..6" inside each box packs
    # the digit into the cell as its own blob — air3 shipped with a literal "3" in the top left.
    # Targeted, not a blanket corner wipe: a SMALL, ACHROMATIC component riding the TOP of the
    # panel. A hood corner is neither small nor grey, so it survives.
    ink2 = out.max(2) < 200
    lab, n = ndimage.label(ink2)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None or sl[0].start > H * 0.45:
            continue
        blob = (lab[sl] == i)
        if not (40 < blob.sum() < 1600):
            continue
        px = out[sl][blob]
        mx, mn = px.max(1), px.min(1)
        sat = np.median(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0))
        if sat < 0.20 and np.median(mx) < 150:
            out[sl][blob] = 255
    return out


def main():
    src, outdir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert('RGB')
    A = np.asarray(im).astype(int)
    bs = bands(A)
    print(f'{src.name}: {len(bs)} figure bands')
    for i, (y0, y1) in enumerate(bs, 1):
        w = walls(A, y0, y1)
        top = max(0, y0 - 32)
        sub = A[top:min(A.shape[0], y1 + 12)].copy()
        Image.fromarray(clean(sub, w).astype('uint8'), 'RGB').save(outdir / f'row{i}.png')
        inner = w[1:-1] if len(w) > 2 else w
        ink = [int((clean(sub, w).max(2) < 200)[:, w[k] + 10:w[k + 1] - 10].sum())
               for k in range(len(w) - 1)] if len(w) > 1 else []
        print(f'  row{i}  y{y0}-{y1}  panels {len(w) - 1}  '
              f'--n {len(w) - 1} --cuts {",".join(str(x) for x in inner)}')
        if ink and min(ink) < 2000:
            print(f'    ⚠ a panel came back nearly empty: {ink} — check before packing')


if __name__ == '__main__':
    main()
