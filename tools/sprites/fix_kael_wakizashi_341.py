"""Shorten one of Kael's two blades on the Aug 2 move-sheet cells — geometrically.

The nano-banana pass returned the matched pair unchanged, the same refusal that built
shorten_wakizashi.py: a still editor will not change a measurement it does not consider
wrong. So the length change is an affine scale along the blade's own axis.

⛔ A BLADE IS THE MERGED SET OF ITS FRAGMENTS, NOT ONE SILVER BLOB. The fist and its
black outline cut every blade into two or three silver pieces, and the first pass fed
single blobs to the shortener — it compressed one FRAGMENT and left the tip floating,
and 40 of 48 frames still read as a matched pair on the montage. Fragments are merged
when one sits on the line through the other's axis; the two biggest merged groups are
the two swords.

⛔ ONLY A MATCHED PAIR IS TOUCHED (ratio >= 0.75 after merging). Shortening an already
short wakizashi again would halve it twice.

Runs on KEYED cells (needs alpha). Usage:
    python3 fix_kael_wakizashi_341.py <keyed_dir> <out_dir>
"""
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

KEEP = 0.5
MIN_FRAG = 80        # px at 3x — smaller silver bits are studs and glints
LINE_TOL = 22        # px: a fragment's centroid must sit this close to the other's axis line
GAP_MAX = 380        # px along the axis between fragment centroids — a full blade at 3x runs
                     # ~260px, so two of its fragments' centroids can sit 200+px apart; 120
                     # left every crossed-behind-the-hand blade unmerged


def silver_fragments(rgba):
    a = rgba[..., :3].astype(int)
    op = rgba[..., 3] > 128
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    lab, n = ndimage.label(op & (mx > 100) & (sat < 0.35), structure=np.ones((3, 3)))
    frags = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < MIN_FRAG:
            continue
        ys, xs = np.nonzero(m)
        pts = np.stack([xs, ys]).astype(float)
        c = pts.mean(1)
        u, s, _ = np.linalg.svd(pts - c[:, None], full_matrices=False)
        frags.append({'m': m, 'c': c, 'ax': u[:, 0], 'elong': s[0] / max(s[1], 1e-6)})
    return frags


def merge_blades(frags):
    """Union fragments that lie on one line — the line of the more elongated one."""
    n = len(frags)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            a, b = frags[i], frags[j]
            ref = a if a['elong'] >= b['elong'] else b
            oth = b if ref is a else a
            d = oth['c'] - ref['c']
            dist = np.hypot(*d)
            if dist > GAP_MAX:
                continue
            along = abs(d @ ref['ax'])
            perp = np.sqrt(max(dist ** 2 - along ** 2, 0))
            if perp < LINE_TOL:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(frags[i])
    blades = []
    for g in groups.values():
        m = np.zeros_like(g[0]['m'])
        for f in g:
            m |= f['m']
        ys, xs = np.nonzero(m)
        pts = np.stack([xs, ys]).astype(float)
        c = pts.mean(1)
        u, s, _ = np.linalg.svd(pts - c[:, None], full_matrices=False)
        t = (xs - c[0]) * u[0, 0] + (ys - c[1]) * u[1, 0]
        blades.append({'m': m, 'c': c, 'ax': u[:, 0], 'len': float(t.max() - t.min()),
                       'n': int(m.sum())})
    blades.sort(key=lambda b: -b['n'])
    return blades[:2]


def shorten_mask(rgba, m, c, axis):
    """The affine compress from shorten_wakizashi, on a merged mask."""
    ys, xs = np.nonzero(m)
    t = (xs - c[0]) * axis[0] + (ys - c[1]) * axis[1]
    body = np.nonzero(rgba[..., 3] > 128)
    bc = np.array([body[1].mean(), body[0].mean()])
    lo = c + axis * t.min()
    hi = c + axis * t.max()
    guard, tip = (lo, hi) if np.hypot(*(lo - bc)) < np.hypot(*(hi - bc)) else (hi, lo)
    d = tip - guard
    L = np.hypot(*d)
    d = d / L
    perp = np.array([-d[1], d[0]])
    H, W = m.shape
    gy, gx = np.mgrid[0:H, 0:W]
    rel = np.stack([gx - guard[0], gy - guard[1]])
    u = rel[0] * d[0] + rel[1] * d[1]
    v = rel[0] * perp[0] + rel[1] * perp[1]
    su = u / KEEP
    sx = np.rint(guard[0] + su * d[0] + v * perp[0]).astype(int)
    sy = np.rint(guard[1] + su * d[1] + v * perp[1]).astype(int)
    ok = (su >= 0) & (su <= L) & (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    ok &= np.where(ok, m[np.clip(sy, 0, H - 1), np.clip(sx, 0, W - 1)], False)
    new = rgba.copy()
    alone = m & ~ndimage.binary_dilation((rgba[..., 3] > 128) & ~m, np.ones((5, 5)))
    new[alone] = 0
    new[ok] = rgba[np.clip(sy, 0, H - 1)[ok], np.clip(sx, 0, W - 1)[ok]]
    return new, L


def main():
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(src.glob('*.png')):
        rgba = np.array(Image.open(p).convert('RGBA'))
        bl = merge_blades(silver_fragments(rgba))
        if len(bl) < 2:
            Image.open(p).save(dst / p.name)
            print(f'  {p.name}: {len(bl)} blade(s) after merge — passed through')
            continue
        ratio = min(bl[0]['len'], bl[1]['len']) / max(bl[0]['len'], bl[1]['len'])
        if ratio < 0.75:
            Image.open(p).save(dst / p.name)
            print(f'  {p.name}: already unequal ({ratio:.2f}) — kept as-is')
            continue
        # the katana is the one held HIGH; shorten the lower blade
        low = max(bl, key=lambda b: b['c'][1])
        new, L = shorten_mask(rgba, low['m'], low['c'], low['ax'])
        img = Image.fromarray(new, 'RGBA')
        img.crop(img.getbbox()).save(dst / p.name)
        print(f'  {p.name}: merged blade {L:.0f}px -> {L * KEEP:.0f}px  (pair ratio was {ratio:.2f})')


if __name__ == '__main__':
    main()
