"""Shorten one of Kael's two blades to a wakizashi — geometrically, not by prompt.

Owner ruling, Aug 1 2026: ONE LONG KATANA + ONE SHORT WAKIZASHI, never a matched
pair. His Twin Rising Fang row came back with both blades the same length, and TWO
nano-banana passes returned the frame unchanged both times (the second with an
explicit "HALF, not three-quarters" instruction). A still editor will not reliably
change a measurement it does not consider wrong.

So do it as what it is — an affine scale along the blade's own axis, anchored at the
guard. Width is untouched, which is exactly right: a wakizashi is a SHORTER blade,
not a thinner one, so squashing only the long axis produces a real short sword and
keeps the tip's drawn shape instead of inventing one.

The blade is found, not clicked: silver is the only low-saturation bright material on
a black-and-gold character, and of the silver blobs the target is the one whose hand
sits LOWER in the frame (his raised hand carries the katana in every pose here).

⛔ ERASE ONLY WHAT IS OVER EMPTY AIR. Blanking the whole old blade would punch a hole
through the body wherever the blade crossed it. The old blade is cleared only where
nothing else is drawn underneath, and the warped blade is then composited back on
top — so a blade that passes in front of the hood leaves the hood intact.
"""
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

KEEP = 0.5          # new blade length, as a fraction of the old
MIN_BLADE = 300     # px; smaller silver blobs are studs, glints and hilt furniture


def blades(rgba):
    a = rgba[..., :3].astype(int)
    op = rgba[..., 3] > 128
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    silver = op & (mx > 110) & (sat < 0.30)
    lab, n = ndimage.label(silver, structure=np.ones((3, 3)))
    out = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < MIN_BLADE:
            continue
        ys, xs = np.nonzero(m)
        pts = np.stack([xs, ys]).astype(float)
        c = pts.mean(1, keepdims=True)
        u, s, _ = np.linalg.svd(pts - c, full_matrices=False)
        if s[0] / max(s[1], 1e-6) < 3.0:      # not elongated -> not a blade
            continue
        out.append((m, c[:, 0], u[:, 0], s))
    return out


def shorten(path, out_path):
    im = Image.open(path).convert('RGBA')
    rgba = np.array(im)
    bl = blades(rgba)
    if len(bl) < 2:
        return f'{path.name}: found {len(bl)} blade(s) — skipped'

    # the katana is the one held HIGH; shorten the other
    bl.sort(key=lambda b: b[1][1])            # by centroid y, top first
    m, c, axis, _ = bl[-1]

    ys, xs = np.nonzero(m)
    t = (xs - c[0]) * axis[0] + (ys - c[1]) * axis[1]
    # the guard end is the end nearer the body's ink centroid
    body = np.nonzero(rgba[..., 3] > 128)
    bc = np.array([body[1].mean(), body[0].mean()])
    lo = c + axis * t.min()
    hi = c + axis * t.max()
    guard, tip = (lo, hi) if np.hypot(*(lo - bc)) < np.hypot(*(hi - bc)) else (hi, lo)
    d = (tip - guard)
    L = np.hypot(*d)
    d = d / L
    perp = np.array([-d[1], d[0]])

    H, W = m.shape
    gy, gx = np.mgrid[0:H, 0:W]
    rel = np.stack([gx - guard[0], gy - guard[1]])
    u = rel[0] * d[0] + rel[1] * d[1]          # along the blade
    v = rel[0] * perp[0] + rel[1] * perp[1]    # across it
    su = u / KEEP                              # sample further out to compress
    sx = np.rint(guard[0] + su * d[0] + v * perp[0]).astype(int)
    sy = np.rint(guard[1] + su * d[1] + v * perp[1]).astype(int)
    ok = (su >= 0) & (su <= L) & (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    ok &= np.where(ok, m[np.clip(sy, 0, H - 1), np.clip(sx, 0, W - 1)], False)

    new = rgba.copy()
    # clear the old blade ONLY where it is the only thing drawn (over empty air)
    alone = m & ~ndimage.binary_dilation(
        (rgba[..., 3] > 128) & ~m, np.ones((5, 5)))
    new[alone] = 0
    new[ok] = rgba[np.clip(sy, 0, H - 1)[ok], np.clip(sx, 0, W - 1)[ok]]

    img = Image.fromarray(new, 'RGBA')
    img.crop(img.getbbox()).save(out_path)
    return f'{path.name}: blade {L:.0f}px -> {L * KEEP:.0f}px'


def main():
    for p in sys.argv[1:]:
        p = pathlib.Path(p)
        print('  ' + shorten(p, p))


if __name__ == '__main__':
    main()
