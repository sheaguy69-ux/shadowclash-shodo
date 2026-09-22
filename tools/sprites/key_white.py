"""Key a flat-white still-editor output to RGBA and trim it.

nano-banana hands back a 2K RGB frame on a white page. Everything downstream — the
eye-scale measurement, the geometric blade edit, the packer — assumes a trimmed RGBA
cell, and running any of them on the raw RGB silently treats the whole page as
foreground. (It did: the first blade pass ran on an un-keyed frame, where "bright and
unsaturated" matches the page as readily as the steel.)

⛔ A HARD CUT OFF A WHITE SHEET LEAVES A WHITE HALO — the same trap pack_kael_
spreadsheet documents. Every edge pixel is a blend of ink and page; a binary key keeps
the 90%-page ones at full opacity and, on the game's dark stage, that reads as a lit
outline traced round the character. So the alpha is RAMPED across the blend range and
the blend is then undone (c = (p - (1-a)*page) / a), which gives a half-covered pixel
the ink's own colour at half alpha instead of a washed-out one at full.

Largest connected component only: the still editor likes to leave a stray speck in a
corner, and a speck 900px from the body would set the trim box.
"""
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

TOL = 34      # colour distance from white that counts as ink at all
KNEE = 150    # ...and where the ramp reaches full opacity
PAGE = np.array([255, 255, 255])


def key(path):
    a = np.array(Image.open(path).convert('RGB')).astype(float)
    dist = np.sqrt(((a - PAGE) ** 2).sum(2))
    fg = dist > TOL
    lab, n = ndimage.label(fg, np.ones((3, 3)))
    if n:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        keep = np.zeros_like(fg)
        for i, sz in enumerate(sizes):
            if sz > 400 or i == int(sizes.argmax()):   # body, plus limbs/blades
                keep |= lab == i + 1
        fg = keep
    al = np.clip((dist - TOL) / (KNEE - TOL), 0, 1) * fg
    rgb = np.clip((a - (1 - al)[..., None] * PAGE) / np.maximum(al, 1e-3)[..., None], 0, 255)
    im = Image.fromarray(np.dstack([rgb, al * 255]).astype('uint8'), 'RGBA')
    return im.crop(im.getbbox())


def main():
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(src.glob('*.png')):
        im = key(p)
        im.save(dst / p.name)
        print(f'  {p.name}: {im.width}x{im.height}')


if __name__ == '__main__':
    main()
