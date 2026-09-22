#!/usr/bin/env python3
"""Append already-keyed owner-spreadsheet cells to a fighter's sheet.

`extend_sheet.py` takes RAW white frames and derives the scale from a base image.
The owner's move spreadsheets arrive already cut (`cut_sheet_grid.py`), shadow-erased
and keyed, and each sheet is drawn at its own size on the page — so the scale is per
SHEET, measured once against the idle's body height, and applied to every cell in it.

⛔ ONE UNIFORM SCALE PER SHEET, never per cell. Per-cell height matching makes a
compact pose (a crouch, an apex) come out the same height as a stretched one and the
character boils between frames.

Append-only: the existing sheet is pasted in byte-identical and verified after the
write. New cells land at cols, cols+1, ... and the manifest gains one key per frame.

Usage:
  python3 pack_owner_cells.py <fighter> <keyed_dir> <anchor_row> row1 row2 ...
    anchor_row: the row whose frame 1 is a neutral standing pose; the scale is
                idle-body-height / that frame's height.
  python3 pack_owner_cells.py <fighter> <keyed_dir> =<scale> row1 row2 ...
    an explicit scale instead of the anchor. Needed when the sheet has NO standing
    pose to anchor on — an all-aerial sheet is the case that forced this. Body height
    against a standing idle is meaningless there: every frame is a tuck or a dive, so
    the anchor measures the pose. Those scales come from matching INK AREA against the
    fighter's own air1/air2/air3, which is pose-alike and rotation-invariant, and were
    each confirmed by eye on an area-matched contact sheet before being written down.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[2]
SPRITES = REPO / 'web/assets/sprites'


def body_h(im):
    a = np.array(im)[:, :, 3] > 16
    ys, _ = np.nonzero(a)
    return int(ys.max() - ys.min() + 1)


def main():
    fighter, keyed, anchor, rows = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4:]
    jp, pp = SPRITES / f'{fighter}.json', SPRITES / f'{fighter}.png'
    man = json.loads(jp.read_text())
    W, H, FY, cols = man['frameW'], man['frameH'], man['footY'], man['cols']
    sheet = Image.open(pp).convert('RGBA')
    original = sheet.crop((0, 0, cols * W, H)).tobytes()

    idle = sheet.crop((man['frames']['idle'] * W, 0, (man['frames']['idle'] + 1) * W, H))
    if anchor.startswith('='):
        scale = float(anchor[1:])
        print(f'{fighter}: uniform scale {scale:.4f} (given — no standing pose to anchor on)')
    else:
        scale = body_h(idle) / Image.open(keyed / f'{anchor}_1.png').height
        print(f'{fighter}: idle body {body_h(idle)}px, uniform scale {scale:.4f}')

    new = [(f'{r}{i}', keyed / f'{r}_{i}.png') for r in rows for i in range(1, 7)]
    out = Image.new('RGBA', ((cols + len(new)) * W, H), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))     # paste, NOT alpha_composite: compositing rewrites the
                                 # RGB under transparent pixels and the originals stop
                                 # being byte-identical.
    for n, (key, path) in enumerate(new):
        im = Image.open(path).convert('RGBA')
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)
        idx = cols + n
        out.alpha_composite(im, (idx * W + (W - im.width) // 2, FY - im.height))
        man['frames'][key] = idx

    assert out.crop((0, 0, cols * W, H)).tobytes() == original, 'original cells changed'
    man['cols'] = cols + len(new)
    out.save(pp)
    jp.write_text(json.dumps(man, indent=2) + '\n')
    print(f'  +{len(new)} cells -> cols {cols} to {man["cols"]}  ({new[0][0]}..{new[-1][0]})')


if __name__ == '__main__':
    main()
