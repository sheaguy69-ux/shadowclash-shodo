#!/usr/bin/env python3
"""Put Oni's claw on the SAME hand in every cell, by mirroring — no redraw.

    python3 tools/sprites/normalize_claw.py <cells...> --out <dir> [--side L]

THE PROBLEM: his claw gauntlet is on one hand only, and the generator cannot hold
which one. Measured across a delivered 32-cell matrix: claw left in 16 cells, right
in 10, ambiguous in 5. The identity lock says right hand, always.

⛔ MIRRORING SWAPS ANATOMY. A mirrored figure holds the claw in the OTHER hand — that
is the whole point of the owner's rule "never mirror the claw onto the left hand". So
the target side is not "whatever the majority does", it is fixed by his main reference:
front-facing, claw on the VIEWER'S LEFT, which is HIS RIGHT hand. Normalising to the
majority instead of to the reference puts the claw on his left hand in every cell and
fails checklist items 1, 2 and 4 at once. Default --side is L for that reason.

THE FIX IS FREE, because he is symmetric everywhere else. Hood, horns, mask, the two
X-crossed katanas and the armour all read identically flipped — verified by eye on
four cells — so mirroring a cell moves the claw to the other hand and changes nothing
a viewer can name. That is cheaper than redrawing and it is exact.

It also disarms the engine's mirror problem. `ctx.scale(-p.facing, 1)` flips the whole
sprite on a side change, which would otherwise put a right-hand claw on his left. Once
every cell is normalised, the per-cell `mirror` map can pin handedness in either facing.

FINDING THE CLAW: talons are LONG THIN protrusions, so they are what survives when you
subtract the eroded body core from the silhouette. Score that thin mass either side of
the core's centroid. A cell with too little thin mass has no visible claw at all — the
generator dropped it — and is reported, never flipped, because mirroring cannot add a
claw that was never drawn. Those are the only cells that need art.
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd


def claw_side(A, thin_min=40, ratio=1.35):
    """-> ('L'|'R'|'mixed'|'none', left_px, right_px)"""
    op = A[:, :, 3] > 0
    if op.sum() < 200:
        return ('none', 0, 0)
    core = nd.binary_erosion(op, np.ones((3, 3)), iterations=4)
    if core.sum() < 50:
        return ('none', 0, 0)
    thin = op & ~nd.binary_dilation(core, np.ones((3, 3)), iterations=4)
    _, cx = nd.center_of_mass(core)
    xs = np.where(thin)[1]
    if xs.size < thin_min:
        return ('none', 0, 0)
    L, R = int((xs < cx).sum()), int((xs >= cx).sum())
    if L > R * ratio:
        return ('L', L, R)
    if R > L * ratio:
        return ('R', L, R)
    return ('mixed', L, R)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cells', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--side', choices=['L', 'R'], default='L',
                    help="viewer-side the claw must end up on. DEFAULT 'L': the main "
                         "reference is front-facing with the claw on the VIEWER'S LEFT, "
                         "which is HIS RIGHT hand. Getting this backwards silently "
                         "produces the exact violation the owner's checklist forbids.")
    a = ap.parse_args()
    d = pathlib.Path(a.out)
    d.mkdir(parents=True, exist_ok=True)

    flipped = kept = missing = ambiguous = 0
    no_claw = []
    for p in a.cells:
        p = pathlib.Path(p)
        A = np.asarray(Image.open(p).convert('RGBA')).astype(int)
        side, L, R = claw_side(A)
        out = A
        if side == 'none':
            missing += 1
            no_claw.append(p.stem)
        elif side == 'mixed':
            ambiguous += 1
        elif side != a.side:
            out = A[:, ::-1]
            flipped += 1
        else:
            kept += 1
        Image.fromarray(out.astype(np.uint8)).save(d / p.name)
        print(f'{p.stem:<26} {side:<6} L={L:<5} R={R:<5} '
              f'{"FLIPPED" if out is not A else ""}')

    print(f'\nkept {kept} · flipped {flipped} · ambiguous {ambiguous} · '
          f'no claw drawn {missing}')
    if no_claw:
        print('\n⛔ NO CLAW IN THESE — mirroring cannot fix them, they need art:')
        for n in no_claw:
            print(f'   {n}')


if __name__ == '__main__':
    main()
