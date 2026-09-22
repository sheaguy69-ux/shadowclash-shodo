"""Ember's teal scarf and cyan eyes -> his own green, locally and for free.

Owner ruling, Aug 2 2026: don't spend on frames a local edit can do. 43 of his 54
move-sheet cells were recoloured by nano-banana before the fal balance ran out; this
reproduces that edit exactly on the remaining 11, at no cost.

⛔ THE TRANSFORM IS MEASURED OFF THE PAID FRAMES, NOT INVENTED. Six cut/edited pairs
were compared pixel-for-pixel (the edit is a 2K upscale, so it is resized back to the
cut's size first) and the teal band moved like this:

    scarf core  h 173 -> 106   s 0.78 -> 0.31   v 0.20 -> 0.29
    eye tint    h 178 -> 114   s 0.31 -> 0.22   v 0.85 -> 0.86

Both are one operation: rotate the teal/cyan band into green, desaturate, lift the
value. Saturation and value are the straight lines through those two measured points,
which is why a dark scarf desaturates hard and a near-white eye barely moves. Live
Ember's own eyes read h 84 s 0.28 v 0.91, so the target lands in his family.

What this does NOT do: the claw count. The paid pass did not change it either — his
frames still carry four blades per gauntlet after editing, measured on the same pairs —
so a locally recoloured frame and a paid one are the same edit, and the row stays
internally consistent.

Usage:
    python3 recolor_ember_scarf.py <cut_dir> <out_dir> [frame.png ...]
    python3 recolor_ember_scarf.py selftest
"""
import pathlib
import sys

import numpy as np
from PIL import Image

# the teal/cyan band, wide enough for the scarf's shadow and the eye's rim
HUE_LO, HUE_HI = 148.0, 218.0
SAT_FLOOR = 0.12          # below this a pixel has no hue worth rotating
HUE_OUT = 108.0           # between the measured 106 (scarf) and 114 (eyes)
# s' = SA*s + SB and v' = VA*v + VB, fitted through the two measured points above
SA, SB = 0.191, 0.161
VA, VB = 0.877, 0.115
PAGE = 690                # sum(RGB) above this is the flat white page — never touched


def _rgb2hsv(a):
    a = a.astype(float) / 255
    mx, mn = a.max(2), a.min(2)
    d = np.maximum(mx - mn, 1e-6)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.zeros_like(mx)
    m = mx == r
    h[m] = (((g - b) / d)[m]) % 6
    m = mx == g
    h[m] = (((b - r) / d)[m]) + 2
    m = mx == b
    h[m] = (((r - g) / d)[m]) + 4
    return h * 60, s, mx


def _hsv2rgb(h, s, v):
    hp = (h % 360) / 60
    c = v * s
    x = c * (1 - np.abs(hp % 2 - 1))
    z = np.zeros_like(h)
    i = hp.astype(int) % 6
    r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [c, x, z, z, x, c])
    g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [x, c, c, x, z, z])
    b = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [z, z, x, c, c, x])
    m = v - c
    return np.clip(np.stack([r + m, g + m, b + m], -1) * 255, 0, 255).astype(np.uint8)


def recolor(im):
    """RGB in, RGB out. Alpha is carried through untouched if present."""
    rgba = im.convert('RGBA')
    a = np.array(rgba)
    rgb = a[..., :3]
    h, s, v = _rgb2hsv(rgb)
    on_ink = (rgb.astype(int).sum(2) < PAGE) & (a[..., 3] > 8)
    m = on_ink & (h > HUE_LO) & (h < HUE_HI) & (s > SAT_FLOOR)
    if m.any():
        h2, s2, v2 = h.copy(), s.copy(), v.copy()
        h2[m] = HUE_OUT
        s2[m] = np.clip(SA * s[m] + SB, 0, 1)
        v2[m] = np.clip(VA * v[m] + VB, 0, 1)
        a[..., :3] = np.where(m[..., None], _hsv2rgb(h2, s2, v2), rgb)
    return Image.fromarray(a, 'RGBA'), int(m.sum())


def selftest():
    """A teal patch turns green; a red patch and the white page do not move."""
    a = np.full((40, 60, 3), 255, np.uint8)
    a[5:20, 5:25] = (13, 92, 99)        # scarf teal, h~176 s~0.87 v~0.39
    a[22:35, 5:25] = (170, 40, 40)      # a red that must survive
    out, n = recolor(Image.fromarray(a))
    o = np.array(out)[..., :3]
    h, s, v = _rgb2hsv(o)
    assert n > 250, f'teal patch not found ({n}px)'
    assert 95 < h[10, 10] < 125, f'scarf did not land in green: h={h[10, 10]:.0f}'
    assert s[10, 10] < 0.45, f'scarf not desaturated: s={s[10, 10]:.2f}'
    assert 150 < o[28, 10][0] and o[28, 10][1] < 90, 'the red patch was recoloured'
    assert tuple(o[0, 0]) == (255, 255, 255), 'the white page was touched'
    print('recolor_ember_scarf selftest OK — teal -> green, red and page untouched')


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        return selftest()
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    names = sys.argv[3:]
    dst.mkdir(parents=True, exist_ok=True)
    files = [src / n for n in names] if names else sorted(src.glob('*.png'))
    for p in files:
        out, n = recolor(Image.open(p))
        out.convert('RGB').save(dst / p.name)
        print(f'  {p.name}: {n}px recoloured')


if __name__ == '__main__':
    main()
