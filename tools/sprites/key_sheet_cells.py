#!/usr/bin/env python3
"""Key a whole directory of cut spreadsheet cells — the house recipe, in one place.

    python3 tools/sprites/key_sheet_cells.py <cut_dir> <out_dir>

Every pack_*.py so far inlined these same six lines; `cut_sheet_grid.py` now feeds
three sheets at a time, so it lives here once.

The recipe, in this order, because the order is load-bearing:

  1. fuzz 42% corner floodfill. 42, not 25 — the owner's sheets carry a soft drop
     shadow under the figure and 25 leaves a grey plate welded to the feet.
  2. keep the LARGEST connected component. Floodfill only reaches the field the corner
     can walk to; a shadow that touches the body, an FX spark sitting in a gap and the
     row's ruled line all survive step 1 as islands. This is what deletes them.
  3. purge sub-visible alpha LAST. Doing it before step 2 breaks the component apart at
     its own anti-aliased outline and the "largest blob" becomes a shoulder.

A cell that keys to nothing is an error, not an empty PNG — a silently blank frame packs
as a hole in the middle of a move.
"""
import os
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage

FUZZ = 42
ALPHA_FLOOR = 16       # below this the pixel is invisible on screen; keep it out of the bbox


def key(src: pathlib.Path) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        dst = t.name
    # the 1px white border is what lets the floodfill get around a ruled line that the
    # cutter left clipped to the very edge of the cell
    subprocess.run(['magick', str(src), '-alpha', 'set',
                    '-bordercolor', 'white', '-border', '1',
                    '-fuzz', f'{FUZZ}%', '-fill', 'none', '-floodfill', '+0+0', 'white',
                    '-shave', '1x1', dst], check=True)
    im = Image.open(dst).convert('RGBA')
    a = np.array(im)
    solid = a[..., 3] > ALPHA_FLOOR
    lab, n = ndimage.label(ndimage.binary_closing(solid, np.ones((3, 3))))
    if not n:
        raise SystemExit(f'{src.name}: keyed to nothing — check the sheet background')
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    a[..., 3] *= (lab == int(np.argmax(sizes)) + 1)
    a[..., 3] = _drop_shadow_pocket(a)
    a[..., 3][a[..., 3] <= ALPHA_FLOOR] = 0
    out = Image.fromarray(a, 'RGBA')
    # NOCROP=1 keeps the source canvas — pack_shodo_row computes a shared window across
    # beats in board coordinates, and beats cropped to their own bboxes break it (PIL
    # pads out-of-bounds crops with BLACK, which packed as a solid bar).
    if os.environ.get('NOCROP'):
        return out
    return out.crop(out.split()[3].getbbox())


def _drop_shadow_pocket(a):
    """Delete the white pocket the drop shadow encloses between the feet.

    The corner floodfill can only reach the field it can WALK to. The owner's ground rows
    are drawn with a soft grey shadow under the figure, and the bright centre of that
    shadow is walled off from the corner by the shadow's own darker rim — so it survives
    step 1 as a solid white plate welded between the ankles, and step 2 keeps it because
    it is part of the largest component. On a checkerboard it reads as the fighter
    standing on a slab of paper.

    The rule that separates it from the character's own greys: EVERY GREY THAT BELONGS TO
    A FIGHTER IS FENCED BY A BLACK OUTLINE. Mizu's eyes, Shin's steel shuriken, a blade
    highlight and a scarf edge are all enclosed by ink and never border the transparent
    field. The shadow has no outline of its own, so its blob runs straight into
    transparency. Touching the outside is the test; brightness alone is not — the pocket
    measured 151-255 on Shin's ground rows, which is exactly his shuriken's range, and a
    brightness-only rule ate the weapon.
    """
    alpha = a[..., 3]
    rgb = a[..., :3].astype(int)
    near_white = (alpha > ALPHA_FLOOR) & (rgb.max(2) - rgb.min(2) < 30) & (rgb.mean(2) > 150)
    if not near_white.any():
        return alpha
    outside = np.pad(alpha <= ALPHA_FLOOR, 1, constant_values=True)
    touches = (outside[:-2, 1:-1] | outside[2:, 1:-1] | outside[1:-1, :-2] | outside[1:-1, 2:])
    lab, n = ndimage.label(near_white)
    if not n:
        return alpha
    vis = alpha > ALPHA_FLOOR
    body = float(vis.sum())
    # measured against the SILHOUETTE's own box, never the canvas — the cell is mostly
    # empty page, so "the bottom 18%" of the canvas is well below the fighter's feet and
    # the test never fires
    by, bx = np.nonzero(vis)
    top, h = by.min(), by.max() - by.min() + 1
    w = bx.max() - bx.min() + 1
    kill = np.zeros(n + 1, bool)
    for i in range(1, n + 1):
        blob = lab == i
        if blob.sum() < 0.01 * body:
            continue                       # an anti-aliased sliver, not a plate
        ys, xs = np.nonzero(blob)
        # Either the blob runs into the transparent field (an open pocket), or it sits
        # UNDER THE FEET and is wide. The second test is needed because the darker rim of
        # the same shadow can seal the bright core off from the field entirely — that is
        # Shin's ground rows, where the plate never touches the outside and a
        # touch-only rule left all ten of them standing on a slab of paper.
        kill[i] = bool((blob & touches).any()) or (ys.min() - top > 0.82 * h
                                                   and xs.max() - xs.min() + 1 > 0.25 * w)
    return alpha * ~kill[lab]


def selftest():
    """The shadow plate goes, the steel weapon stays.

    Both are low-saturation grey in the same brightness band — Shin's plate measured
    151-255 and his shuriken sits inside that — so brightness alone cannot tell them
    apart, and a brightness-only rule ate the weapon. What separates them is the black
    outline: the weapon has one, the shadow does not.
    """
    a = np.full((120, 100, 3), 255, np.uint8)
    a[20:90, 30:70] = (40, 90, 40)               # the body
    a[40:60, 60:85] = 20                         # a black-outlined...
    a[44:56, 64:81] = 190                        # ...grey steel weapon
    a[92:104, 20:80] = 200                       # the drop shadow's bright plate, no outline
    a[90:93, 20:80] = 120                        # its darker rim, sealing it from the page
    src = pathlib.Path(tempfile.mktemp(suffix='.png'))
    Image.fromarray(a).save(src)
    out = np.array(key(src))
    src.unlink()
    grey = (out[..., 3] > ALPHA_FLOOR) & (out[..., :3].astype(int).mean(2) > 150) \
        & (out[..., :3].astype(int).max(2) - out[..., :3].astype(int).min(2) < 30)
    assert grey.sum() > 100, f'the outlined steel weapon was erased with the shadow ({grey.sum()}px left)'
    assert out.shape[0] < 80, f'the shadow plate survived — frame is still {out.shape[0]}px tall'
    print('key_sheet_cells selftest OK — shadow plate erased, outlined steel weapon kept')


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        return selftest()
    cut, outdir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    files = sorted(cut.glob('*.png'))
    assert files, f'no cells in {cut}'
    for f in files:
        key(f).save(outdir / f.name)
    print(f'{cut.name}: keyed {len(files)} cells -> {outdir}')


if __name__ == '__main__':
    main()
