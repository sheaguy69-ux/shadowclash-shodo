#!/usr/bin/env python3
"""Take the stone wall out of a wall-cling / wall-jump cell, keeping the fighter.

    python3 tools/sprites/strip_wall.py <cell.png> [<cell.png> ...] --out <dir>

The owner drew the wall-cling poses against a stone slab so the grip reads. The game
draws its own walls, so the slab has to come off — and it CANNOT come off with a crop,
because his claw hand and foot claws are drawn ON the slab; cropping to the right of it
amputates the exact detail the pose exists to show ("the wall-cling uses foot claws to
let ONI stay perfectly still on the wall").

So the slab is removed by what it IS, not by where it is:

  * find it as the tallest run of near-full-height opaque columns in the left third —
    a wall spans the cell top to bottom, a fighter does not;
  * inside that band drop NEUTRAL MID-GREY (the stone fill and its mortar), which his
    parts are not: his overlapping bits are black ink, dark cloth, or bright wrapping;
  * then drop what is left of the slab's own dark OUTLINE — a column inside the band
    that is still nearly full height after the fill is gone is the wall's edge, never
    a limb, because no part of him is a 1-3px full-height stripe;
  * keep the largest remaining component so freed stone specks do not ship.

Verified on both cling cells: slab gone, claw and foot claws intact.
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd


def band_of(op, W):
    """Longest run of near-full-height opaque columns, ANYWHERE across the cell.

    An earlier version scanned only the left third, because on the first wall board the
    slab was always left of him. It is not: on the second board he pushes off slabs that
    sit to his RIGHT, and a left-third scan finds nothing and silently ships the wall.
    A wall is identified by being full-height, not by which side it is on.
    """
    frac = op.mean(0)
    best, s = (0, 0), None
    lim = W
    for x in range(lim):
        if frac[x] > 0.90:
            if s is None:
                s = x
        elif s is not None:
            if x - s > best[1] - best[0]:
                best = (s, x)
            s = None
    if s is not None and lim - s > best[1] - best[0]:
        best = (s, lim)
    return best


def strip(A):
    op = A[:, :, 3] > 0
    rgb = A[:, :, :3]
    H, W = op.shape
    a, b = band_of(op, W)
    if b - a < 3:
        return A, 0, (a, b)

    band = np.zeros_like(op)
    band[:, a:b] = True
    v = rgb.mean(2)
    spread = rgb.max(2) - rgb.min(2)

    stone = band & op & (v >= 62) & (v <= 165) & (spread <= 14)
    stone = (nd.binary_dilation(stone, np.ones((3, 3))) & op & band
             & (v >= 55) & (spread <= 20))

    # ⛔ COLOUR ALONE IS NOT A WALL — IT ATE HIS FACE. His WHITE MASK is shaded with
    # neutral greys that sit squarely inside the stone band, so the colour test claimed part
    # of it: measured on the cling cell, 547 of 2340 mask pixels were removed and the sprite
    # shipped with a hole punched through the left of his face. The fix protects the MASK
    # rather than weakening the stone test — requiring the stone to be a full-height slab
    # was tried and removed the real wall too (0px stripped on all six cells). His mask is
    # the one thing on him that is BRIGHT and neutral, so find it, grow it by 3px to cover
    # its own shaded rim, and make it untouchable. Everything else about the wall pass is
    # unchanged, so the slab still comes off exactly as before.
    face = op & (v >= 190) & (spread <= 45)
    keep = np.zeros_like(face)
    if face.any():
        lab, n = nd.label(face)
        sizes = nd.sum(face, lab, range(1, n + 1))
        for j in range(1, n + 1):
            if sizes[j - 1] >= 120:          # the mask, not a stray highlight
                keep |= (lab == j)
        if keep.any():
            stone &= ~nd.binary_dilation(keep, np.ones((3, 3)), iterations=3)

    out = A.copy()
    out[stone, 3] = 0

    # the slab's own outline: still-full-height columns inside the band
    op2 = out[:, :, 3] > 0
    for x in range(a, b):
        if op2[:, x].mean() > 0.80:
            out[:, x, 3] = 0

    # ⚠ LOOSE BRICK PAST THE SLAB IS STILL THERE, AND IS LEFT ALONE ON PURPOSE. The
    # boards carry mortar and brick drawn outside the full-height core, and a colour test
    # cannot lift it: measured on the cling cell, the brick band overlaps his own armour and
    # cloak (his dark cloth samples v~1-50, the mortar v~100-160, with the ranges touching),
    # so any threshold wide enough to take the brick also bites him. The house rule is that
    # a background pass never damages the body, so this waits for either a wall-free redraw
    # or a hand mask — it is NOT worth risking his silhouette. It sits where the game draws
    # its own wall anyway, so it reads as wall rather than as an artefact.
    m = out[:, :, 3] > 0
    lab, n = nd.label(m)
    if n > 1:
        sz = nd.sum(m, lab, range(1, n + 1))
        keep = int(np.argmax(sz)) + 1
        out[(lab != keep) & (lab != 0), 3] = 0
    return out, int(stone.sum()), (a, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cells', nargs='+')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    d = pathlib.Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    for p in a.cells:
        A = np.asarray(Image.open(p).convert('RGBA')).astype(int)
        out, removed, (b0, b1) = strip(A)
        m = out[:, :, 3] > 0
        if not m.any():
            print(f'{pathlib.Path(p).name}: EVERYTHING removed — skipped')
            continue
        ys, xs = np.where(m)
        crop = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        Image.fromarray(crop.astype(np.uint8)).save(d / pathlib.Path(p).name)
        print(f'{pathlib.Path(p).name}: band x{b0}-{b1}, {removed}px stone -> '
              f'{crop.shape[1]}x{crop.shape[0]}')


if __name__ == '__main__':
    main()
