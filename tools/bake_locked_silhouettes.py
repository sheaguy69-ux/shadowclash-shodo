#!/usr/bin/env python3
"""Bake solid black silhouettes of benched fighters from their ink portraits.

The portraits are opaque paintings on cream paper, so the figure is whatever is not
paper. Output is a transparent PNG (black figure, alpha = shape) at
<out>/ninjas/locked/<name>.png - the path lockedPortraitSrc() already reads.
Only the outline survives; no colour, no face, no weapon detail.
usage: bake_locked_silhouettes.py <web-dir> <out-dir> exile mokurai
"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

def bake(src, dst, size=320):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    paper = np.median(np.concatenate([a[:12].reshape(-1, 3), a[-12:].reshape(-1, 3)]), axis=0)
    ink = np.abs(a - paper).sum(axis=2) > 60
    ink = ndi.binary_closing(ink, iterations=6)
    ink = ndi.binary_fill_holes(ink)
    lab, n = ndi.label(ink)
    if n > 1:                                   # drop stray flecks, keep the figure
        sizes = ndi.sum(ink, lab, range(1, n + 1))
        ink = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * 0.02])
    mask = Image.fromarray((ink * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(2))
    mask = mask.point(lambda v: 255 if v > 127 else 0).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new('RGBA', mask.size, (0, 0, 0, 0)); out.putalpha(mask)
    out = out.resize((size, size), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True); out.save(dst, optimize=True)

if __name__ == '__main__':
    web, out, *names = sys.argv[1:]
    for n in names:
        bake(f'{web}/assets/ninjas/{n}.png', f'{out}/assets/ninjas/locked/{n}.png')
        print('baked', n)
