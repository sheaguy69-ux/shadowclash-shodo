#!/usr/bin/env python3
"""Cut the grey training dummy out of a cell. He is standing NEXT TO Oni, so cut
where the two figures stop touching and keep the side Oni is on.

    python3 tools/sprites/cut_dummy.py <cell.png> [...] --out <dir>

Two things that look simpler and are not, both measured on these boards:

  * "Drop the grey." The dummy carries the SAME heavy black outline Oni does — that
    is the medium law for every figure on the page — so colour keeps his outline and
    only hollows him out.
  * "Keep the biggest blob." The razor wire physically joins them in most cells, so
    Oni and the dummy are ONE blob and nothing separates.

What is actually true is positional: they are two bodies side by side, and the only
ink spanning the space between them is the wire, which is thin. So score each column
by how TALL its ink is, cut at the thinnest column between the two bodies, and keep
the side holding his WHITE MASK — the one thing on the page the dummy does not have.
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd


def mask_blob(A):
    """His white demon mask: bright, near-neutral, and a real blob rather than a speck."""
    op = A[:, :, 3] > 0
    rgb = A[:, :, :3].astype(int)
    v, spread = rgb.mean(2), rgb.max(2) - rgb.min(2)
    white = op & (v >= 185) & (spread <= 45)
    lab, n = nd.label(white)
    if not n:
        return None
    sizes = nd.sum(white, lab, range(1, n + 1))
    j = int(np.argmax(sizes)) + 1
    if sizes[j - 1] < 60:
        return None
    return lab == j


def strip(A):
    op = A[:, :, 3] > 0
    H, W = op.shape
    m = mask_blob(A)
    if m is None:
        return A, 0, None                    # no mask found: refuse to guess which is him
    _, mx = np.nonzero(m)
    mask_cx = int(mx.mean())

    height = op.sum(0).astype(float)          # how TALL the ink is in each column
    body = height > H * 0.22                  # a standing figure, not a wire

    # ⛔ THEY OFTEN TOUCH, so "find the gap between two column-runs" is not enough — in the
    # close-in and finish cells the two bodies overlap and the column profile never breaks,
    # which read as "one figure only" and shipped the dummy. The anchor that always holds is
    # HIS MASK: whatever mass of body-columns sits well away from it is the other figure, and
    # the cut goes at the lowest column between the two centres, touching or not.
    far = body.copy()
    far[max(0, mask_cx - 55):mask_cx + 55] = False
    if not far.any():
        return A, 0, None                     # only him in this cell — nothing to cut

    lab, n = nd.label(far)
    sizes = [int((lab == j).sum()) for j in range(1, n + 1)]
    keep = np.ones(W, bool)
    cuts = []
    for j, sz in enumerate(sizes, 1):
        if sz < 12:                           # a stray arm or FX column, not a body
            continue
        xs = np.nonzero(lab == j)[0]
        other_cx = int(xs.mean())
        a, b = (mask_cx, other_cx) if other_cx > mask_cx else (other_cx, mask_cx)
        cut = a + int(np.argmin(height[a:b + 1]))
        cuts.append(cut)
        if other_cx > mask_cx:
            keep[cut:] = False
        else:
            keep[:cut + 1] = False
    if not cuts:
        return A, 0, None

    out = A.copy()
    out[:, ~keep, 3] = 0
    kx = np.nonzero(keep)[0]
    return out, int(W - keep.sum()), (int(kx.min()), int(kx.max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cells', nargs='+')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    d = pathlib.Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    for p in a.cells:
        A = np.asarray(Image.open(p).convert('RGBA')).astype(np.uint8)
        out, cols, span = strip(A)
        m = out[:, :, 3] > 0
        if not m.any():
            print(f'{pathlib.Path(p).name}: nothing left — skipped')
            continue
        ys, xs = np.where(m)
        crop = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        Image.fromarray(crop).save(d / pathlib.Path(p).name)
        note = f'kept x{span[0]}-{span[1]}, {cols} columns cut' if span else 'one figure only'
        print(f'{pathlib.Path(p).name}: {note} -> {crop.shape[1]}x{crop.shape[0]}')


def _selfcheck():
    """A grey figure beside a masked one, joined by a thin wire: the grey goes, the
    wire's stub goes with it, and every pixel of him survives."""
    A = np.zeros((60, 120, 4), np.uint8)
    A[14:54, 10:40] = (20, 20, 24, 255)        # him
    A[18:30, 16:34] = (240, 240, 240, 255)     # his white mask
    A[14:54, 80:110] = (140, 140, 140, 255)    # the dummy, standing apart
    A[32:35, 40:80] = (200, 20, 10, 255)       # the wire joining them
    him = int((A[:, :, 3] > 0)[:, :40].sum())     # his BODY columns; x40+ is the wire

    op = A[:, :, 3] > 0
    lab, n = nd.label(op)
    assert n == 1, 'the wire must make them ONE blob, or this test proves nothing'

    out, cols, span = strip(A)
    o = out[:, :, 3] > 0
    assert o[:, 80:].sum() == 0, 'dummy survived'
    assert o[:, :40].sum() == him, f"his pixels changed: {o[:, :40].sum()} vs {him}"
    assert span[0] == 0 and 39 <= span[1] < 80, span   # span is the KEPT extent, not the cut
    print(f'selfcheck OK — one joined blob, kept x{span[0]}-{span[1]}, dummy gone, his pixels intact')


if __name__ == '__main__':
    import sys
    if '--selfcheck' in sys.argv:
        _selfcheck()
    else:
        main()
