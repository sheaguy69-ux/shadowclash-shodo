"""Pick ONE scale per fighter for a new sheet, anchored on the EYE, not on height.

The ledger's own lesson (326 / 331 / 332): height-matching is valid only when the new
art is an EDIT of a packed cell. These sheets were drawn independently, so matching
total height inflates every head — 332 measured body height at 0.118/0.858/1.407/1.353
for ember/mizu/shin/tsubasa and the correct head-picked answers were 0.130/1.00/1.20/1.30.

The eye is the one feature that is rigid across poses: it does not crouch, stretch,
rotate with a blade, or hide under a cape. Its span between two drawings of the same
character is therefore the size ratio, and nothing else.

⛔ THE GOLD-TRIM TRAP (Kael, 322's failed pass). A naive "bright saturated blob" grab
reads his gold sash and trim as eyes and answers nonsense. The documented filter is
kept: a blob only counts as an eye if the ring of pixels just outside it is mostly
DARK — an eye sits in a black faceless hood, a sash sits on a lit body.

⛔ THE FX TRAP (683's refuted pass). Ring polarity alone still passed a gold slash arc,
a blade glint and a scarf tail as "the eye" on attack rows. Three more rules now gate
every candidate, all scale-free: it sits in the HEAD BAND of the ink bbox, it is ENCLOSED
by ink (an eye lives inside a hood; FX and scarf tails touch the silhouette edge), and
it is DISC-shaped (fill of its bbox, aspect) at the fighter's known eye/ink area FRACTION.
A cell whose landmark fails any gate returns [] — a row takes the median of what was
found, and a caller must treat a row with fewer than half its cells found as unmeasured.

⛔ THE PIXEL FLOOR (Sep 2 2026 re-validation, post-keyer packed cells). The landmarks are
6-13px across. Six size estimators (hard area, linear / glow-cut sub-pixel coverage over a
3px and 5px halo, coverage second moments, 4x bicubic re-threshold) all agree on the idle
spread to within 0.5%: tsubasa 3.5-4.3%, mizu 4.2-5.6%, ember 5.2-5.6%, shin 5-8%. That
spread is the drawing (a one-pixel anti-alias ring on a 10px disc is 4%), not the
estimator, so only the executioner's 12.5px amber pair clears the 3% gate. Inter-eye
distance was tried for the pair fighters and is WORSE (7.8%: the head turns).

Median across the frames given, so one odd pose cannot set the scale.
"""
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

# Per fighter: hue window (deg; lo>hi wraps through 0), saturation window, min brightness,
# ring polarity ('dark' = a glowing eye inside a black hood, 'bright' = a red mark on a
# pale face), `band` = the head band as a fraction of the ink bbox (hair spikes, a staff
# or a tall hood push the eye down the bbox: tsubasa/mizu 0.45, shin 0.55), `frac` = the
# landmark's hard-pixel area / ink area measured on the packed idle (candidates within
# 0.2x..5x of it; linear 0.45x..2.2x). `pair` = both eyes always visible, total of the
# two (a lone blob is NOT trusted: the main eye was lost). `rim` = the landmark is a ring
# around a centre the keyer may have punched out — see _rim.
EYE = {
    'executioner': dict(hue=(28, 60),  smin=0.25, vmin=150, frac=0.0040, pair=True, band=0.50, fill=0.35),   # amber pair (pale, sat ~0.3 on the special row; the front wedge fills ~0.4 of its box; a raised blade pushes the head to mid-bbox — 0.50 keeps special 197 at 0.37 and drops the wrist glint of 196 at 0.55); hood trim is hue 24 / dim
    'kael':        dict(hue=(30, 60),  smin=0.30, vmin=80,  frac=0.0058, band=0.32),   # small gold clasp in the hood; trim ring fails `fill`
    'ember':       dict(smax=0.15, frac=0.0067),                                       # single white eye (placeholder doll until gk_ packs)
    'mizu':        dict(smax=0.15, frac=0.0060, band=0.45, pair=True),                 # white pair; staff tip raises the bbox
    'shin':        dict(hue=(165, 215), smin=0.12, vmin=70, frac=0.0110, band=0.55, rim=True),  # blue rim; centre is keyed / white / navy per row
    'tsubasa':     dict(smax=0.15, frac=0.0069, band=0.45),                            # single white eye; run hair spikes raise the bbox
    'oni':         dict(hue=(340, 20), smin=0.45, vmin=100, frac=0.0012, ring='bright', pair=True, fill=0.35),  # red SLIT eyes in the white mask (fill ~0.4 of their box)
    'exile':       dict(hue=(340, 22), smin=0.55, vmin=110, frac=0.0033, ring='bright', enclosed=False, fill=0.40),  # red crest on the white headband (keyer eats the band around it); her real eye is an amber iris at hue 28-32 / sat 0.45-0.6 — the SAME colour as her skin, not separable
    'mokurai':     dict(hue=(340, 25), smin=0.65, vmin=90,  frac=0.0016, ring='bright', aspect=3.2),  # red forehead dot on the bone mask (a 5x10 oval); the closed-eye slits are 6x5px, smaller still
}
# Fighters whose landmark did NOT validate on the packed sheets (Sep 2 2026, post-keyer,
# 8 idle+xidle cells unless noted): the tool still measures them, but a scale taken from
# them is a guess, not a ruler. Executioner is the only validated eye ruler (idle 2.6%,
# xnuki 1.026 vs area 1.029).
UNMEASURABLE = {
    'kael':    'clasp is ~50px hard; idle spread 16.2%; adown 0.826 vs area 0.693 (3/8 found)',
    'ember':   'placeholder doll; idle spread 5.4%; run_clean 1/8 found; gk_ art not packed',
    'mizu':    'idle spread 4.4%; the pair turns with the head (special reads 0.744 at area 1.002, 7/8)',
    'shin':    'idle spread 6.5%; disc size follows the row (run_clean 1.149 at area 1.178, sneu 1.392 at 1.357, 2/8)',
    'tsubasa': 'idle spread 3.8%; eye drawn 1.099x on run_clean (area 0.998) and 1.269x on divecut (area 0.832); gsfwd 0.875 vs area 0.662 (3/8)',
    'oni':     'two idle cells only (6.2/6.3px, 1.0%); run_clean 0/8 and dive 0/6 found',
    'exile':   'crest is 30-38px hard on a keyer-eaten band; idle spread 18.5% (cell 62 = 7.96 vs xidle 6.67-7.25)',
    'mokurai': 'forehead dot is 12-17px hard; idle spread 9.2%; brun 0.893 vs area 0.852 (8/8)',
}
DEF = dict(hue=None, smin=0.0, smax=1.0, vmin=150, ring='dark', band=0.35, frac=None,
           fill=0.45, aspect=2.5, enclosed=True, pair=False, rim=False)


def _colour_mask(a, cfg):
    op = a[..., 3] > 128
    rgb = a[..., :3].astype(float)
    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    m = op & (mx > cfg['vmin']) & (sat >= cfg['smin']) & (sat <= cfg['smax'])
    if cfg['hue']:
        hue = np.array(Image.fromarray(a[..., :3], 'RGB').convert('HSV'))[..., 0].astype(float) * 360 / 255
        lo, hi = cfg['hue']
        m &= ((hue >= lo) & (hue <= hi)) if lo <= hi else ((hue >= lo) | (hue <= hi))
    return op, rgb, m


def _rim_disc(op, m):
    """Shin: the eye is a blue RING; its centre is keyed out on idle/run cells, navy or
    white on the special. The landmark is the DISC the ring bounds: rim pixels, plus the
    keyed-out pocket they enclose (a 1-2px break in the rim is closed first), plus any
    opaque centre. Returns (disc mask, rim mask); the caller demands that a disc carries
    enough rim to be a ring and not a bare keyer pocket."""
    rim = ndimage.binary_closing(m, np.ones((3, 3))) | m
    pocket = ndimage.binary_fill_holes(ndimage.binary_closing(op, np.ones((5, 5)))) & ~op
    pocket &= ndimage.binary_dilation(rim, np.ones((3, 3)))          # only pockets touching a rim
    pocket = ndimage.binary_fill_holes(pocket | rim) & ~rim           # the whole enclosed centre
    return ndimage.binary_fill_holes(rim | pocket), rim


def eyes(img, cfg):
    """ONE landmark size for the cell as a 1-list (or [] when nothing qualifies).

    Size = equivalent diameter 2*sqrt(A/pi). A is sub-pixel COVERAGE: every pixel of the
    blob plus its 1px halo is projected on the colour line ring->eye, then mapped
    0.25->0, 0.75->1 (glow tail cut), so an anti-aliased edge counts fractionally (a
    12px eye is quantised to whole pixels by a threshold — an 8% step).
    Gates, all scale-free: colour window; centroid in the head band; area within
    0.2x..5x of frac*ink; enclosed by ink; fill >= 0.45 of its bbox and aspect <= 2.5;
    ring polarity. cfg['pair']: the largest survivor plus a mate >= 0.25x its size
    BESIDE it (within 2.5 diameters across, 1 down — a trim spot up the hood is not a
    mate; the executioner's front wedge is ~0.3x), else [] — a lone blob means the main
    eye was lost. cfg['rim']: the blob is the disc of _rim_disc; its rim pixels must run
    at least ~40% of the circumference and fill under 70% of the disc (a ring, not a
    bare keyer pocket, not a solid scarf fold).
    eyes.last keeps (size, span, cx, cy, hard-pixel area) of the picked blobs for QC;
    eyes.rejected keeps (reason, area, cx, cy) of every candidate that failed a gate.
    """
    cfg = {**DEF, **cfg}
    a = np.array(img.convert('RGBA'))
    op, rgb, m = _colour_mask(a, cfg)
    if not op.any():
        return []
    ink = int(op.sum())
    top, bot = np.nonzero(op.any(1))[0][[0, -1]]
    rim = None
    if cfg['rim']:
        m, rim = _rim_disc(op, m)
        op = op | m
    lab, n = ndimage.label(ndimage.binary_fill_holes(m), np.ones((3, 3)))
    # the size window is a FRACTION of the drawing, not a pixel count: the same eye is
    # ~200px across on a 2K still-editor return and ~16px in a packed cell.
    lo, hi = (cfg['frac'] * ink * 0.2, cfg['frac'] * ink * 5) if cfg['frac'] else (max(6, ink * 0.0004), ink * 0.06)
    dark = cfg['ring'] == 'dark'
    white = cfg['smax'] < 0.5
    found = []
    eyes.rejected = []
    for i in range(1, n + 1):
        b = lab == i
        area = int(b.sum())
        if area < 4:
            continue
        ys, xs = np.nonzero(b)
        h, w = np.ptp(ys) + 1, np.ptp(xs) + 1
        halo = ndimage.binary_dilation(b, np.ones((3, 3)))
        ring = ndimage.binary_dilation(b, np.ones((7, 7))) & ~halo & op
        lum = rgb[ring].sum(1)
        why = None
        if not (lo < area < hi):
            why = 'size'
        elif ys.mean() > top + (bot - top) * cfg['band']:   # head band: sash, bracers, blade highlights all live below
            why = 'band'
        elif area < cfg['fill'] * h * w or max(h, w) > cfg['aspect'] * min(h, w):   # a disc, not a trim curve or a glint
            why = f'shape fill={area / (h * w):.2f} asp={max(h, w) / min(h, w):.1f}'
        elif rim is not None and not (1.2 * 2 * np.sqrt(area / np.pi) < (b & rim).sum() < 0.7 * area):   # a ring, not a bare keyer pocket and not a solid teal scarf fold
            why = f'rim {int((b & rim).sum())}px of {area}'
        elif cfg['enclosed'] and (halo & ~op).any():          # FX arcs and scarf tails touch the silhouette
            why = 'not enclosed'
        elif ring.sum() < 12:
            why = 'no ring'
        # the hood is black; trim is not. A mark on a pale face has a pale ring cut by
        # its own dark outline, so 'bright' asks for less of the ring.
        elif (dark and (lum < 210).mean() < 0.50) or (not dark and (lum > 300).mean() < 0.25):
            why = f'ring dark={(lum < 210).mean():.2f} bright={(lum > 300).mean():.2f}'
        if why:
            eyes.rejected.append((why, area, float(xs.mean()), float(ys.mean())))
            continue
        edge = halo & op
        if rim is not None:                                    # rim mode: the centre counts whole, only the ring edge is soft
            edge &= ~(b & ~rim)
        src = rgb[b & rim] if rim is not None else rgb[b]
        e, r = np.median(src, 0), np.median(rgb[ring][(lum < 210) if dark else (lum > 300)], 0)
        t = ((rgb[edge] - r) @ (e - r)) / max(float((e - r) @ (e - r)), 1)
        # coverage with the glow tail cut: a pixel 3/4 of the way to the eye colour counts
        # whole, 1/4 of the way counts nothing (a glowing eye's halo varies frame to frame
        # and a plain clip(t) sum drifted with it — measured 3.9% -> 2.6% on exec idle)
        size = float(np.clip((t - 0.25) / 0.5, 0, 1).sum()) + (0 if rim is None else int((b & ~rim).sum()))
        found.append((size, int(max(h, w)), float(xs.mean()), float(ys.mean()), area))
    if not found:
        return []
    found.sort(reverse=True)
    picked = found[:1]
    if cfg['pair']:
        d1 = 2 * np.sqrt(found[0][0] / np.pi)
        mate = [f for f in found[1:] if f[0] >= 0.25 * found[0][0]
                and abs(f[2] - found[0][2]) < 2.5 * d1 and abs(f[3] - found[0][3]) < d1]   # beside the main eye, not a trim spot up the hood
        if not mate:
            return []
        picked = [found[0], mate[0]]
    eyes.last = picked
    eyes.found = found
    return [float(2 * np.sqrt(sum(f[0] for f in picked) / np.pi))]


def keyed(a):
    """The engine keys cells at DRAW time (keyedShodoCell): if >30% of the ink bbox
    perimeter is ink, the dominant colour bucket is a card and everything reachable from
    the bbox edge that is near-transparent or within tolerance of it is cleared. Measure
    what the owner sees, never the file alpha. (Byte-equal to the scratchpad keyer_emu
    port on all 1415 referenced cells of the nine sheets.)"""
    a = a.copy()
    op = a[..., 3] >= 8
    if not op.any():
        return a
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    rect = op[y0:y1 + 1, x0:x1 + 1]
    edge = rect[0].sum() + (rect[-1].sum() if y1 != y0 else 0)
    if y1 > y0 + 1:
        edge += rect[1:-1, 0].sum() + (rect[1:-1, -1].sum() if x1 != x0 else 0)
    if edge <= (2 * rect.shape[1] + 2 * max(0, rect.shape[0] - 2)) * 0.30:
        return a
    cell = a[y0:y1 + 1, x0:x1 + 1]
    solid = cell[..., 3] >= 128
    if not solid.any():
        return a
    rgb = cell[..., :3][solid].astype(int)
    bucket = (rgb[:, 0] >> 5) * 64 + (rgb[:, 1] >> 5) * 8 + (rgb[:, 2] >> 5)
    b = np.bincount(bucket, minlength=512).argmax()
    card = rgb[bucket == b].mean(0)
    mean = card.mean()
    tol = 40 if mean < 45 else (80 if mean < 140 else 110)
    dist2 = ((cell[..., :3].astype(int) - card) ** 2).sum(2)
    floodable = (cell[..., 3] >= 8) & ~((cell[..., 3] >= 220) & (dist2 > tol * tol))
    lab, n = ndimage.label(floodable)
    border = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    seen = np.isin(lab, border[border > 0])
    if seen.sum() > rect.size * 0.12:
        cell[..., 3][seen] = 0
    return a


def measure(paths, cfg):
    vals = []
    for p in paths:
        vals += eyes(Image.open(p), cfg)
    return float(np.median(vals)) if vals else 0.0


def main():
    fighter = sys.argv[1]
    new = [pathlib.Path(p) for p in sys.argv[2:]]
    cfg = EYE[fighter]
    repo = pathlib.Path(__file__).resolve().parents[2]
    import json
    d = json.loads((repo / f'web/assets/sprites/{fighter}.json').read_text())
    sh = np.array(Image.open(repo / f'web/assets/sprites/{fighter}.png').convert('RGBA'))
    w = d['frameW']
    # canon = the idle/xidle STAND beats as packed, post-keyer (single-row sheet: cell c at x=c*w)
    ref = sorted({i for k, i in d['frames'].items() if k in ('idle', 'idle2') or k.startswith('xidle')})
    vals = [v for i in ref for v in eyes(Image.fromarray(keyed(sh[:, i * w:(i + 1) * w])), cfg)]
    old = float(np.median(vals or [0]))
    nw = measure(new, cfg)
    if fighter in UNMEASURABLE:
        print(f'⛔ {fighter}: eye ruler NOT validated — {UNMEASURABLE[fighter]}. Use the ink-area ruler and look.')
    print(f'{fighter}: shipped eye {old:.1f}px ({len(vals)}/{len(ref)} idle cells)   new-art eye {nw:.1f}px   '
          f'-> scale {old / nw if nw else 0:.4f}')


if __name__ == '__main__':
    main()
