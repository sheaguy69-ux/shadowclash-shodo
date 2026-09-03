#!/usr/bin/env python3
"""Exact Python port of the engine's runtime keyer (keyedShodoCell, index.html:1662).

The owner judges frames POST-keyer — every scan/render must go through this first.
Port is line-faithful: bbox on alpha>=8, perimeter edge-ink > 30% arms the card path,
512-bucket histogram (3 bits/channel, alpha>=128) picks the card colour, tolerance by
mean (<45: 40, <140: 80, else 110), BFS flood from bbox edge seeds where a pixel is
floodable if alpha<220 OR within tol of the card colour, applied only if the flood
covers >12% of the rect.
"""
import numpy as np
from collections import deque


def keyed_cell(a):
    """a: HxWx4 uint8. Returns a copy with the runtime keyer applied."""
    a = a.copy()
    d = a.reshape(-1, 4)
    H, W = a.shape[:2]
    alpha = a[:, :, 3]
    op = alpha >= 8
    if not op.any():
        return a
    ys, xs = np.where(op)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    perimeter = 2 * (x1 - x0 + 1) + 2 * max(0, y1 - y0 - 1)
    edge_ink = int(op[y0, x0:x1 + 1].sum())
    if y1 != y0:
        edge_ink += int(op[y1, x0:x1 + 1].sum())
    if y1 > y0 + 1:
        edge_ink += int(op[y0 + 1:y1, x0].sum())
        if x1 != x0:
            edge_ink += int(op[y0 + 1:y1, x1].sum())
    # A card FILLS its cell. Already-keyed art arrives mostly transparent and its ink
    # bbox hugs the figure, so a pose can trip the perimeter test with no card present.
    clear = int((alpha < 8).sum())
    if clear >= H * W * 0.70 or edge_ink <= perimeter * 0.30:
        return a
    # dominant colour bucket among alpha>=128 inside the rect
    rect = a[y0:y1 + 1, x0:x1 + 1]
    m = rect[:, :, 3] >= 128
    if not m.any():
        return a
    rgb = rect[:, :, :3][m].astype(int)
    buckets = (rgb[:, 0] >> 5) * 64 + (rgb[:, 1] >> 5) * 8 + (rgb[:, 2] >> 5)
    counts = np.bincount(buckets, minlength=512)
    b = int(counts.argmax())
    sel = buckets == b
    br, bg, bb = rgb[sel].mean(0)
    mean = (br + bg + bb) / 3
    tol = 40 if mean < 45 else (80 if mean < 140 else 110)
    tol2 = tol * tol
    seen = np.zeros((H, W), bool)
    q = deque()
    rgbi = a[:, :, :3].astype(int)
    dist2 = ((rgbi[:, :, 0] - br) ** 2 + (rgbi[:, :, 1] - bg) ** 2 + (rgbi[:, :, 2] - bb) ** 2)
    floodable = (alpha >= 8) & (~((alpha >= 220) & (dist2 > tol2)))

    def seed(x, y):
        if 0 <= x < W and 0 <= y < H and not seen[y, x] and floodable[y, x]:
            seen[y, x] = True
            q.append((x, y))
    for x in range(x0, x1 + 1):
        seed(x, y0)
        seed(x, y1)
    for y in range(y0 + 1, y1):
        seed(x0, y)
        seed(x1, y)
    while q:
        x, y = q.popleft()
        if x > x0: seed(x - 1, y)
        if x < x1: seed(x + 1, y)
        if y > y0: seed(x, y - 1)
        if y < y1: seed(x, y + 1)
    if seen.sum() > (x1 - x0 + 1) * (y1 - y0 + 1) * 0.12:
        a[:, :, 3][seen] = 0
    return a


def selftest():
    # a white card with a dark figure: card floods away, figure survives,
    # and the white pocket enclosed by the figure SURVIVES (the flood can't reach it)
    a = np.zeros((100, 80, 4), np.uint8)
    a[5:95, 5:75] = (250, 248, 245, 255)          # card
    a[20:80, 20:60, :3] = 30; a[20:80, 20:60, 3] = 255   # figure block
    a[40:50, 30:40] = (250, 248, 245, 255)        # enclosed pocket
    out = keyed_cell(a)
    assert out[10, 10, 3] == 0, 'card survived'
    assert out[50, 25, 3] == 255, 'figure was eaten'
    assert out[45, 35, 3] == 255, 'pocket unexpectedly reached (fine if flood got there)'
    print('keyer_emu selftest OK — card keyed, figure kept, enclosed pocket LEFT (the class the owner sees)')


if __name__ == '__main__':
    selftest()
