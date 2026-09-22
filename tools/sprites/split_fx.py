#!/usr/bin/env python3
"""Split the owner's red FX off a cell into its own layer, leaving the body clean.

    python3 tools/sprites/split_fx.py <cell.png> ... --out <dir>

writes  <name>.png      the fighter with the FX lifted off
        <name>__fx.png  the FX alone, same canvas, so it composites back exactly

WHY: his claw arcs, slam bursts, speed streaks and smoke are drawn INTO the body cells.
Packed that way they are permanent — they cannot be timed against the active window,
tinted, faded on whiff, scaled with a mode, or drawn behind him. Lifted into their own
layer they become an FX row the engine already knows how to draw, and the body row
stays reusable across moves.

Red is the only hot colour on him, so the split is a colour test — with one exception
that has to be protected: HIS EYES ARE RED. They are saved by where they live, not by
size — an eye sits inside the white mask, an arc does not — so red whose neighbourhood
is mask-white stays with the body. That check is why this is not a one-line threshold.
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd


def split(A, sat=55, level=100):
    op = A[:, :, 3] > 0
    r, g, b = A[:, :, 0], A[:, :, 1], A[:, :, 2]
    red = op & (r > level) & (r - g > sat) & (r - b > sat)

    # protect the eyes: dilate each red blob and ask what surrounds it. Mask white is
    # bright and low-saturation; FX sits on cloth, armour or open air, never in a
    # white field. Blobs are judged whole because an eye is only a few dozen px.
    white = op & (A[:, :, :3].min(2) >= 200)
    lab, n = nd.label(red)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() > 400:                      # far too big to be an eye
            continue
        ring = nd.binary_dilation(m, np.ones((5, 5)), iterations=2) & ~m
        if ring.sum() and (white & ring).sum() / ring.sum() > 0.35:
            red[m] = False                     # an eye — belongs to the body

    # ⛔ THE ARCS HAVE PALE CORES. A claw arc is a white-hot streak with red edges, so
    # a pure red test leaves the core behind and the "clean" body still wears white
    # slashes. The core cannot be taken by brightness alone — his mask and hand wraps
    # are bright too — but it can be taken by TINT: measured on claw_slash, bright
    # pixels beside the arc average saturation 19.2 (warm), while bright pixels
    # elsewhere on him average 3.7 (dead neutral). So absorb bright WARM pixels that
    # sit against the red, and leave bright neutral ones on the body.
    rgb = A[:, :, :3]
    v = rgb.mean(2)
    sat = rgb.max(2) - rgb.min(2)
    halo = nd.binary_dilation(red, np.ones((7, 7)), iterations=2) & ~red & op
    red = red | (halo & (v >= 150) & (sat >= 10))

    body = A.copy()
    body[red, 3] = 0
    fx = A.copy()
    fx[~red, 3] = 0
    return body, fx, int(red.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cells', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--sat', type=int, default=55)
    a = ap.parse_args()
    d = pathlib.Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    for p in a.cells:
        p = pathlib.Path(p)
        A = np.asarray(Image.open(p).convert('RGBA')).astype(int)
        body, fx, n = split(A, sat=a.sat)
        Image.fromarray(body.astype(np.uint8)).save(d / p.name)
        if n:
            Image.fromarray(fx.astype(np.uint8)).save(d / f'{p.stem}__fx.png')
        print(f'{p.name}: {n}px of FX lifted' if n else f'{p.name}: no FX')


if __name__ == '__main__':
    main()
