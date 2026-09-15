"""Key a white REVIEW CARD to RGBA, keeping his eye and losing the paper.

Same ramped key as tools/sprites/key_white.py (a hard cut off white leaves a lit halo
on the ash stage), plus the one thing that tool does not do: ENCLOSED POCKETS SURVIVE.
His eye is near-white ink sitting inside a black head, so a distance-from-white key
calls it page and punches a hole through his face — the documented 708 bug. Every
not-page region that does not touch the image border is interior and is restored at
full alpha with its own colour, EXCEPT a pocket big enough to be real negative space
(Ember's paper slab between the boots, 796), which is reported and dropped.
"""
import sys, pathlib, numpy as np
from PIL import Image
from scipy import ndimage

TOL, KNEE = 34, 150
PAGE = np.array([255., 255., 255.])
POCKET_MAX = 0.06        # of body ink; above this a pocket is negative space, not a landmark
# ...and ABOVE ALL, WHERE IT SITS. His landmarks are high on the body - the eye at 0.28-0.47
# of figure height, blade steel to about 0.7 - while the page that gets trapped between his
# boots always lands at 0.85-0.92. Measured across three boards: every slab was 1028-4630px
# at rel 0.89-0.91, every eye 245-376px at rel 0.28-0.47. A pocket in the boot band is paper.
BOOT_BAND = 0.88
SLAB_MIN  = 400          # ...and both numbers are tuned against MEASURED pockets, not guessed.
# The rush board forced the second correction: its beat 7 traps a 545px slab at rel 0.91,
# under the 600 a coarser pass had used. Depth is the sharper signal. Every real slab
# measured across four boards sits at 0.89-0.91; the one thing that must NOT be eaten, the
# white core of the intro's slash arc, sits at 0.82 and is 453px. 0.88 and 400 clear both.

def key(p):
    a = np.array(Image.open(p).convert('RGB')).astype(float)
    dist = np.sqrt(((a - PAGE) ** 2).sum(2))
    fg = dist > TOL
    lab, n = ndimage.label(fg, np.ones((3, 3)))
    if n:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        keep = np.zeros_like(fg)
        for i, sz in enumerate(sizes):
            if sz > 400 or i == int(sizes.argmax()):
                keep |= lab == i + 1
        fg = keep
    al = np.clip((dist - TOL) / (KNEE - TOL), 0, 1) * fg
    rgb = np.clip((a - (1 - al)[..., None] * PAGE) / np.maximum(al, 1e-3)[..., None], 0, 255)

    # --- enclosed pockets ---------------------------------------------------
    hole = ~fg
    hl, hn = ndimage.label(hole)
    border = set(hl[0]) | set(hl[-1]) | set(hl[:, 0]) | set(hl[:, -1]); border.discard(0)
    body = fg.sum()
    ys = np.nonzero(fg.any(1))[0]; y0, y1 = ys.min(), ys.max()
    filled = 0; dropped = []
    for i in range(1, hn + 1):
        if i in border: continue
        m = hl == i
        py, _ = np.nonzero(m)
        rel = (py.mean() - y0) / max(y1 - y0, 1)
        if m.sum() > POCKET_MAX * body or (rel > BOOT_BAND and m.sum() > SLAB_MIN):
            dropped.append((int(m.sum()), round(float(rel), 2))); continue
        al[m] = 1.0
        rgb[m] = a[m]            # the eye is white; it stays white
        filled += int(m.sum())
    im = Image.fromarray(np.dstack([rgb, al * 255]).astype('uint8'), 'RGBA')
    return im, dict(body=int(body), pockets_filled=filled, pockets_dropped=dropped)

src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
for p in sorted(src.glob('frame-*.png')):
    im, st = key(p)
    im.save(dst / p.name)
    a = np.array(im)
    nearwhite = int(((a[..., :3].min(2) > 200) & (a[..., 3] > 200)).sum())
    print(f'  {p.name} {im.width}x{im.height} body={st["body"]} pockets_kept={st["pockets_filled"]}'
          f' dropped={st["pockets_dropped"]} near-white-kept={nearwhite}')
