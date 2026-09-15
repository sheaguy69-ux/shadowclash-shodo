"""Erase the drawn GROUND BAR from the v1 round-start intro cards.

These cards are painted with a sumi floor stroke: a dark horizontal brush mark running
edge to edge under the boots. It is not a cast shadow the keyer can wash out - it is ink,
as dark as he is - and 798 ruled every drawn ground shadow off the roster, so it cannot
pack. It is also the LOWEST ink on the card, so a foot-anchored pack would weld the BAR
to the floor and leave his boots hovering above it.

Separated by shape, not by colour, because colour cannot tell it from him: in the bottom
band a BOOT column carries a long vertical run of ink (a sole is tall) and a BAR column
carries a short one (a brush stroke is thin). Erase only the short bottom runs, and only
those that reach the very floor. Nothing above the band is touched - the ink above the
boot line is asserted byte-identical.
"""
import sys, pathlib, numpy as np
from PIL import Image

BAND = 18       # px above the lowest ink that counts as the floor band
MAX_RUN = 10    # a bottom run this short is a brush stroke, not a sole
REACH = 12      # ...and it has to actually reach the floor

def scrub(p):
    im = Image.open(p).convert('RGB')
    a = np.array(im); ink = a.mean(2) < 205
    y1 = int(np.nonzero(ink.any(1))[0].max())
    out = a.copy(); wiped = 0
    for x in range(ink.shape[1]):
        col = ink[:, x]
        if not col.any(): continue
        b = int(np.nonzero(col)[0].max())
        if b < y1 - BAND or b < y1 - REACH: continue
        r, y = 0, b
        while y >= 0 and col[y]: r += 1; y -= 1
        if r > MAX_RUN: continue                 # a boot: leave it alone
        out[b - r + 1:b + 1, x] = 255            # back to page
        wiped += r
    keep = ink.copy(); keep[y1 - BAND:] = False  # everything above the floor band
    assert (a[keep] == out[keep]).all(), 'body ink was touched'
    return Image.fromarray(out), wiped, int(keep.sum())

src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
for p in sorted(src.glob('frame-*.png')):
    im, wiped, body = scrub(p)
    im.save(dst / p.name)
    print(f'  {p.name}: bar {wiped}px wiped, body above the band {body}px UNCHANGED')
