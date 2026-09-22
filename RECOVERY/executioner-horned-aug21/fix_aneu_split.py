#!/usr/bin/env python3
"""ANEU beats 7-8 are GROUNDED on an airborne row.

Beat 7 is a kneeling landing and beat 8 a planted ready guard — no edit makes
either airborne, and keying all eight into `aneu` would kneel him in mid-air.
So the row splits where the art splits:

    beats 1-6  -> aneu1..aneu6    the airborne Kesa-giri
    beats 7-8  -> aland1, aland2  the landing tail, drawn only after touchdown

Nothing is discarded — the game had no drawn landing recovery at all, and now
does. The engine plays `aland*` ahead of `aneu*` once `isGrounded` (web/index.html).
This stamps the split onto the board so the keying cannot go wrong later.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = "RECOVERY/executioner-horned-aug21/exec-ANEU-kesa-giri-8f.png"
DST = "RECOVERY/executioner-horned-aug21/exec-ANEU-kesa-giri-6f+LAND2-FIXED.png"
ORANGE, GREY, BLACK = (253, 65, 4), (105, 104, 104), (17, 17, 17)
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
NARROW = "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"

im = Image.open(SRC).convert("RGB")
W, H = im.size
a = np.asarray(im).astype(int)
ink = a.max(2) < 246

# ⛔ measure the split, never hardcode it: the caption columns are the only
# per-beat landmark that never bridges (blades and FX arcs do).
cd = ink[769:923].sum(0)
segs, s = [], None
for x in range(W):
    if cd[x] and s is None: s = x
    if not cd[x] and s is not None:
        if x - 1 - s > 3: segs.append((s, x - 1))
        s = None
cols = []
for x0, x1 in segs:
    if cols and x0 - cols[-1][1] < 30: cols[-1] = (cols[-1][0], x1)
    else: cols.append((x0, x1))
assert len(cols) == 8, f"expected 8 caption columns, found {len(cols)}"
mid = (cols[5][1] + cols[6][0]) // 2
# the caption gap is wider than the art gap — a blade or a trailing scarf reaches
# past its own caption — so snap to the nearest column the FIGURES leave clear.
fig = ink[406:739].sum(0)
free = [x for x in range(cols[5][0], cols[7][1]) if not fig[x]]
assert free, "no clear column between beats 6 and 7"
split = min(free, key=lambda x: abs(x - mid))
assert abs(split - mid) < 40, f"the only clear column is {split}, nowhere near the caption gap {mid}"
print(f"8 caption columns, divider at x={split}")

d = ImageDraw.Draw(im)
# The rule runs only through the rows the board leaves empty — it marks the
# split without a single pixel landing on a drawn beat.
for y0, y1 in [(250, 316), (742, 766), (928, 1004)]:
    for y in range(y0, y1, 14):
        d.line([(split, y), (split, min(y + 8, y1))], fill=GREY, width=3)

def stamp(cx, y, text, font, fill):
    w = d.textlength(text, font=font)
    x = min(max(cx - w / 2, 8), W - w - 8)      # a label that runs off the board is not a label
    d.text((x, y), text, font=font, fill=fill)
    assert x >= 0 and x + w <= W

f28 = ImageFont.truetype(BOLD, 28)
f22 = ImageFont.truetype(NARROW, 26)
lc, rc = (cols[0][0] + cols[5][1]) // 2, (cols[6][0] + cols[7][1]) // 2
stamp(lc, 258, "AIRBORNE", f28, BLACK)
stamp(lc, 290, "aneu1 – aneu6", f22, ORANGE)
stamp(rc, 258, "LANDING TAIL", f28, BLACK)
stamp(rc, 290, "aland1 · aland2", f22, ORANGE)
f20 = ImageFont.truetype(NARROW, 24)
stamp(rc, 950, "grounded only — drawn once he touches down,", f20, GREY)
stamp(rc, 978, "never while he is still in the air", f20, GREY)
stamp(lc, 950, "the six beats that key as the neutral air light", f20, GREY)

im.save(DST)
out = np.asarray(Image.open(DST).convert("RGB")).astype(int)
assert (out[406:739] == a[406:739]).all(), "an art row was touched"
assert (out[107:245] == a[107:245]).all(), "the title was touched"
assert (out[769:923] == a[769:923]).all(), "a caption was touched"
assert (out[319:356] == a[319:356]).all(), "a beat number was touched"
print(f"OK  {DST}  ({(out != a).any(2).sum()} px of annotation, all in free rows)")
