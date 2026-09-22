#!/usr/bin/env python3
"""GLDOWN beat 8: the katana ran off the right edge of the board.

Beat 8 ("Return to ready guard") is the same drawing as beat 1 ("Low ready
guard") — 89.3% IoU on the ink mask at dx=1262, dy=0, and 477 fewer pixels,
which is exactly the tail the canvas cut. So the tip is not invented: it is
lifted from beat 1, which carries the same blade at the same scale, and the
canvas is grown to hold it.

⛔ Every original pixel stays byte-identical. The board only gains paper on
the right plus the 12 columns of blade that were always drawn.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "RECOVERY/executioner-horned-aug21/exec-GLDOWN-sune-giri-8f.png"
DST = "RECOVERY/executioner-horned-aug21/exec-GLDOWN-sune-giri-8f-FIXED.png"
PAD = 24                      # paper past the reconstructed tip
DX, DY_BODY = 1262, 0

a = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
H, W, _ = a.shape
ink = a.max(2) < 246
lab, n = ndimage.label(ink, np.ones((3, 3), bool))
sizes = ndimage.sum(ink, lab, range(1, n + 1))
# beat 1 and beat 8 are the leftmost and rightmost big figure components
big = [i + 1 for i in np.argsort(sizes)[::-1][:8]]
def xmid(c):
    xs = np.where(lab == c)[1]; return (xs.min() + xs.max()) / 2
b1 = min(big, key=xmid); b8 = max(big, key=xmid)
m1, m8 = lab == b1, lab == b8

# the blade sits 2px lower in beat 8 than the body offset — solve it on the
# blade's own columns rather than assuming the body's dy carries.
def seam_err(dy):
    e = 0
    for x in range(1428, 1448):
        y8 = np.where(m8[:, x])[0]; y1 = np.where(m1[:, x - DX])[0]
        if len(y8) and len(y1):
            e += abs((y1.min() + dy) - y8.min()) + abs((y1.max() + dy) - y8.max())
    return e
DY = min(range(-4, 5), key=seam_err)
assert seam_err(DY) < seam_err(DY_BODY) or DY == DY_BODY
print(f"blade dy = {DY} (seam error {seam_err(DY)} vs {seam_err(DY_BODY)} at the body's dy)")

# the tail: every beat-1 column that maps past the old right edge
tail_x1 = [x for x in range(W) if m1[:, x].any() and x + DX >= W]
assert tail_x1, "nothing was clipped — wrong board?"
x1a, x1b = min(tail_x1), max(tail_x1)
ty = np.where(m1[:, x1a:x1b + 1].any(1))[0]
y0, y1 = ty.min() + DY, ty.max() + DY
print(f"reconstructing beat-1 columns {x1a}-{x1b} -> {x1a+DX}-{x1b+DX}, rows {y0}-{y1}")

# ⛔ the tail must be the ONLY ink in that source rectangle, or the paste drags
# a speed line or a caption glyph across with it. The tip's own anti-alias
# fringe reads 243-245 — under the 246 ink threshold, so 3x3 labelling files it
# as its own component. That is the blade, so the mask is the component grown by
# 2px; anything ink and further out than that is genuinely foreign and aborts.
sub = (slice(ty.min(), ty.max() + 1), slice(x1a, x1b + 1))
near = ndimage.binary_dilation(m1, np.ones((5, 5), bool))
assert (ink[sub] & ~near[sub]).sum() == 0, "foreign ink inside the source rectangle"
tip = ink[sub] & near[sub]
print(f"tip mask {int(tip.sum())} px ({int((tip & ~m1[sub]).sum())} of them the sub-246 fringe)")

NW = x1b + DX + 1 + PAD
out = np.full((H, NW, 3), 0, dtype=int)
out[:, :W] = a
# Fill the new columns with the board's OWN paper grain, tiled from a block
# proven clean — not from the strip beside the old edge. That strip reads as
# paper (>=246) but carries the figure's 247-252 anti-alias halo, and copying it
# printed a ghost of beat 8 standing in the margin.
NEW = NW - W
clean = None
for py in range(0, H - 80, 10):
    blk = a[py:py + 80, W - NEW - 8:W - 8]
    if blk.min() >= 252:
        clean = blk; break
assert clean is not None, "no clean paper block on this board"
tile = np.tile(clean, (H // clean.shape[0] + 1, 1, 1))[:H]
out[:, W:] = tile
assert out[:, W:].min() >= 252, "the paper fill is not paper"

paste = a[sub]
pm = tip
sl = out[y0:y1 + 1, x1a + DX:x1b + DX + 1]
sl[pm] = paste[pm]
out[y0:y1 + 1, x1a + DX:x1b + DX + 1] = sl

res = np.clip(out, 0, 255).astype(np.uint8)
assert (res[:, :W] == a.astype(np.uint8)).all(), "an original pixel moved"
Image.fromarray(res).save(DST)

chk = np.asarray(Image.open(DST).convert("RGB")).astype(int)
cink = chk.max(2) < 246
clab, _ = ndimage.label(cink, np.ones((3, 3), bool))
cid = clab[y0 + (y1 - y0) // 2, x1a + DX + 2]
assert cid != 0, "the reconstructed tip is not ink"
assert cid == clab[np.where(m8)[0][0], np.where(m8)[1][0]], \
    "the tip did not join beat 8's figure — the seam has a gap"
comp = clab == cid
xs = np.where(comp)[1]
print(f"OK  {SRC} {W}x{H} -> {DST} {NW}x{H}")
print(f"    beat 8 now spans x{xs.min()}-{xs.max()}, {NW - 1 - xs.max()}px of paper to the edge")
print(f"    {int(comp.sum())} px (was {int(m8.sum())}, beat 1 has {int(m1.sum())})")
