#!/usr/bin/env python3
"""Give a hard-keyed cell the ramped rim that key_white.py gives a raw white page.

    python3 tools/sprites/soft_rim.py <cut_strip_outdir> <outdir>

WHY THIS EXISTS — neither existing tool can do this pair of boards alone:

  cut_strip.py  gets the SILHOUETTE right (pitch cuts, caption drop, neighbour-stub
                drop) but hands back a BINARY alpha. A hard cut off a white sheet keeps
                the 90%-page edge pixels at full opacity, and on the game's dark stage
                that reads as a lit outline traced round the character — the halo
                key_white.py's own docstring warns about.

  key_white.py  gets the RIM right (ramp + un-premultiply) but decides foreground by
                distance from white, so PURE-NEUTRAL WHITE ART IS BACKGROUND TO IT.
                The Sep-2 shodo trio draws Mizu's and Tsubasa's eyes at ~250 neutral,
                so key_white punches both eyes out as holes in every beat.

So take the silhouette from one and the rim from the other: cut_strip's mask is the
AUTHORITY on what is figure (it already survived the enclosed-white question), and the
ramp is applied only where that mask meets the page. Interior stays fully opaque, which
is what keeps a white eye a white eye.

The blend is undone the same way key_white does it — c = (p - (1-a)*page) / a — so a
half-covered pixel gets the ink's own colour at half alpha rather than a washed-out
colour at full alpha.
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd

TOL = 34       # colour distance from page white that counts as ink at all
KNEE = 150     # ...and where the ramp reaches full opacity
MIN_BLOB = 400  # a detached piece smaller than this is a speck, not a limb or FX
PAGE = np.array([255.0, 255.0, 255.0])


def soften(path, tol=TOL, knee=KNEE, min_blob=MIN_BLOB, pad=4):
    a = np.array(Image.open(path).convert('RGBA')).astype(float)
    rgb = a[:, :, :3]
    mask = a[:, :, 3] > 0

    # ⛔ DROP SPECKS BY SIZE, KEEP DETACHED FX. Same rule key_white.py uses: the largest
    # component always survives, and so does anything big enough to be a limb, a blade or
    # a dust plume. Below that floor it is generator noise — on this trio exactly one
    # piece qualified, a 45px grey speck floating beside Mizu's hanbo on INVITE.
    lab, n = nd.label(mask, np.ones((3, 3)))
    if n > 1:
        sizes = nd.sum(mask, lab, range(1, n + 1))
        biggest = int(sizes.argmax())
        keep = np.zeros_like(mask)
        for i, sz in enumerate(sizes):
            if sz >= min_blob or i == biggest:
                keep |= lab == i + 1
        mask = keep

    dist = np.sqrt(((rgb - PAGE) ** 2).sum(2))
    ramp = np.clip((dist - tol) / (knee - tol), 0, 1)

    # Interior is opaque no matter what colour it is — that is the whole point.
    core = nd.binary_erosion(mask, np.ones((3, 3)), iterations=1)
    outer = nd.binary_dilation(mask, np.ones((3, 3)), iterations=2) & ~mask

    al = np.zeros(mask.shape, float)
    al[mask] = 1.0                       # everything the silhouette claims
    edge = mask & ~core
    al[edge] = np.maximum(ramp[edge], 0.35)   # its own outermost ring, softened
    al[outer] = ramp[outer]              # blend pixels the hard key threw away
    al = np.clip(al, 0, 1)
    al[core] = 1.0                       # ...but never eat into the interior

    # ⛔ PURGE SUB-VISIBLE ALPHA LAST. The engine's own keyer treats alpha >= 8 as ink
    # (keyer_emu.keyed_cell), so anything under that is invisible in game but still
    # counts as a component to every QC scan downstream — it shows up as a phantom
    # "detached piece" nobody can see or fix. Measured on Mizu INVITE: one 1px pixel at
    # alpha 6 survived the ramp and read as a second component.
    al[al < 8 / 255] = 0.0

    # ...and re-run the speck filter on the FINISHED alpha, not just the input mask. The
    # ramp mints its own specks: it lifts a faint near-white pixel the hard key had
    # dropped up to alpha 9-15, which clears the threshold above and lands as a 1-3px
    # island (measured on Shin PIERCE and READY). Same size rule, applied where it can
    # see everything.
    vis = al > 0
    lab, n = nd.label(vis, np.ones((3, 3)))
    if n > 1:
        sizes = nd.sum(vis, lab, range(1, n + 1))
        biggest = int(sizes.argmax())
        for i, sz in enumerate(sizes):
            if sz < min_blob and i != biggest:
                al[lab == i + 1] = 0.0

    out = np.clip((rgb - (1 - al)[..., None] * PAGE) / np.maximum(al, 1e-3)[..., None], 0, 255)
    im = Image.fromarray(np.dstack([out, al * 255]).astype('uint8'), 'RGBA')
    im = im.crop(im.getbbox())
    # A tight crop puts ink on all four borders, which every downstream scan reads as a
    # straight cut-off. Pad it back out so the cell carries its own clear margin.
    if pad:
        padded = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        padded.paste(im, (pad, pad))
        im = padded
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--min-blob', type=int, default=MIN_BLOB)
    ap.add_argument('--pad', type=int, default=4, help='transparent margin around the cut')
    a = ap.parse_args()
    src, dst = pathlib.Path(a.src), pathlib.Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(src.glob('*.png')):
        before = np.array(Image.open(p).convert('RGBA'))[:, :, 3] > 0
        im = soften(p, min_blob=a.min_blob, pad=a.pad)
        after = np.array(im)[:, :, 3] > 0
        print(f'  {p.name}: {im.width}x{im.height}  '
              f'solid {int(before.sum())} -> covered {int(after.sum())} '
              f'(+{int(after.sum()) - int(before.sum())} rim px)')
        im.save(dst / p.name)


if __name__ == '__main__':
    main()
