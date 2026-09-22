#!/usr/bin/env python3
"""Edge-stopped background key — for clips whose background is a SMOOTH GRADIENT
that overlaps the character's own values (Seedance gave a grey->black gradient
behind a black-outlined character, so colour/fuzz keying is impossible: measured
bg span 0-201 vs character 0-255).

Principle: the background is SMOOTH, the character has HARD outlines. Grow a
region inward from the frame border through LOW-GRADIENT pixels only; it flows
across the whole gradient and halts at the silhouette. Colour is never used.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage


def key(path, out, grad_thresh=9.0, close=7):
    im = Image.open(path).convert('RGB')
    g = np.asarray(im.convert('L')).astype(float)
    gx = ndimage.sobel(g, 0); gy = ndimage.sobel(g, 1)
    mag = np.hypot(gx, gy) / 4.0
    smooth = mag < grad_thresh                      # candidate background
    # seed from the border, keep only what the border can REACH through smooth pixels
    seed = np.zeros_like(smooth)
    seed[0], seed[-1], seed[:, 0], seed[:, -1] = True, True, True, True
    seed &= smooth
    bg = ndimage.binary_propagation(seed, mask=smooth)
    # the outline itself is high-gradient: dilate bg slightly INTO it, then pull back
    bg = ndimage.binary_closing(bg, np.ones((3, 3)))
    fg = ~bg
    fg = ndimage.binary_closing(fg, np.ones((close, close)))   # seal the outline ring
    fg = ndimage.binary_fill_holes(fg)
    # keep only the largest blob: kills stray specks and the baked ground shadow
    lab, n = ndimage.label(fg)
    if n:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        fg = lab == (int(np.argmax(sizes)) + 1)
    a = np.dstack([np.asarray(im), (fg * 255).astype(np.uint8)])
    o = Image.fromarray(a, 'RGBA')
    bb = o.split()[3].getbbox()
    o.crop(bb).save(out)
    return int(fg.sum())


if __name__ == '__main__':
    print(sys.argv[1], 'opaque px:', key(sys.argv[1], sys.argv[2]))
