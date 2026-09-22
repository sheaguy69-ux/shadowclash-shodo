"""Cut a move spreadsheet whose art BLEEDS ACROSS the cell rules.

`cut_sheet_grid.py` crops tight to the ruled box, which is correct when the artist
kept every frame inside its cell. The Aug 1 sheets did not: a measured pass found
weapons spanning the divider on 8 of 8 rows (Mizu f1-f5, Kael f2-f5, Ember Down+H
f2-f6...). Cropping tight there AMPUTATES the blade at the rule, and the neighbour
inherits a floating fragment of it.

Nothing has to be redrawn for that. Cut WIDE — half a cell of overlap on each side —
then keep the one connected blob that actually belongs to this frame. The overshooting
blade is CONNECTED to its own body, so it comes back whole; the neighbour's fragment
is not connected to anything here, so it drops out. Ownership is decided by which
blob has the most ink inside the true ruled box, not by size: a neighbour leaning in
can out-pixel this frame's crouch.

Usage: python3 cut_sheet_bleed.py "<sheet.png>" <out_dir> <rowname1> [rowname2 ...]
"""
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cut_sheet_grid import PAGE as BG  # ONE page-white constant, shared
from cut_sheet_grid import grid  # the grid finder is already right — reuse it

PAD_X = 0.55      # overlap, as a fraction of one cell's width
PAD_Y = 0.35


def cut(img, rows, cols, r, c):
    """One frame, recovered across the rules."""
    x0, x1 = cols[c + 1], cols[c + 2]
    y0, y1 = rows[r], rows[r + 1]
    px, py = int((x1 - x0) * PAD_X), int((y1 - y0) * PAD_Y)
    W, H = img.size
    wx0, wx1 = max(0, x0 - px), min(W, x1 + px)
    wy0, wy1 = max(0, y0 - py), min(H, y1 + py)

    wide = np.array(img.crop((wx0, wy0, wx1, wy1)).convert('RGB')).astype(int)
    ink = wide.sum(2) < BG

    # the ruled lines are ink too, and they weld every blob into one — drop any
    # column/row that is a thin full-length line before labelling.
    for axis, length in ((0, ink.shape[0]), (1, ink.shape[1])):
        run = ink.sum(axis)
        line = run > length * 0.92
        if axis == 0:
            ink[:, line] = False
        else:
            ink[line, :] = False

    lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
    if n == 0:
        return None

    # this frame's true box, in window coordinates
    ix0, ix1 = x0 - wx0 + 3, x1 - wx0 - 3
    iy0, iy1 = y0 - wy0 + 3, y1 - wy0 - 3
    inside = np.zeros_like(ink)
    inside[iy0:iy1, ix0:ix1] = True

    owned = np.bincount(lab[inside].ravel(), minlength=n + 1)
    owned[0] = 0
    if owned.max() == 0:
        return None
    keep = lab == owned.argmax()

    out = np.full((*keep.shape, 4), 255, np.uint8)
    out[..., :3] = wide.astype(np.uint8)
    out[..., 3] = np.where(keep, 255, 0)
    im = Image.fromarray(out, 'RGBA')
    return im.crop(im.getbbox())


def main():
    src, outdir, names = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3:]
    outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert('RGB')
    rows, cols = grid(img)
    assert len(cols) == 8, f'expected name column + 6 frames, got {len(cols) - 1}: {cols}'
    assert len(rows) - 1 == len(names), f'{len(rows) - 1} rows on the sheet, {len(names)} names'
    for r, name in enumerate(names):
        sizes = []
        for c in range(6):
            im = cut(img, rows, cols, r, c)
            assert im is not None, f'{name}_{c + 1}: nothing found'
            im.save(outdir / f'{name}_{c + 1}.png')
            sizes.append(f'{im.width}x{im.height}')
        print(f'  {name}: {"  ".join(sizes)}')


if __name__ == '__main__':
    main()
