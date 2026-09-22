#!/usr/bin/env python3
"""Grow a fighter's frame box without disturbing a single cell's identity.

    python3 tools/sprites/grow_frame_box.py --sheets web/assets/sprites \
        --name oni --frame-w 480 --frame-h 360 --foot-y 320

⛔ A POSE THAT DOES NOT FIT GROWS THE BOX. Never shrink the body, never crop the
pose — the house rule, and the reason this exists rather than a rescale. The box
is padding; the art inside it is untouched, pixel for pixel.

WHAT IS PRESERVED, because all three are load-bearing:
  * CELL INDEX. frames{} is not rewritten — every key still points at the column
    it pointed at before, so nothing in the engine or in a manifest note goes
    stale. This is the append-only rule's real content: indices are the contract.
  * FOOT LINE. Each cell's lowest opaque pixel is placed on the NEW footY, which
    is what the engine anchors to (anchorFor = (footY - footAdj[i]) * S). A cell
    whose feet were on the old footY is on the new one; a cell that floated by N
    px still floats by N, so genuine air poses keep floating and footAdj entries
    keep meaning the same shortfall.
  * HORIZONTAL PLACEMENT relative to the body centre, so a pose whose FX reaches
    further one way keeps reaching that way.

The manifest's `scale` is NOT touched: it is TARGET_DRAWN / IDLE_BODY_TARGET, a
statement about on-screen size, and has nothing to do with how much empty padding
the cell carries. Growing the box must not change how big he renders.
"""
import argparse
import json
import pathlib

import numpy as np
from PIL import Image


def grow(sheet, man, FW2, FH2, FOOT2):
    FW, FH, FOOT, cols = man['frameW'], man['frameH'], man['footY'], man['cols']
    if FW2 < FW or FH2 < FH:
        raise SystemExit(f'refusing to SHRINK the box ({FW}x{FH} -> {FW2}x{FH2}) — '
                         'that would crop poses, which is the thing this rule exists to stop')
    out = Image.new('RGBA', (FW2 * cols, FH2), (0, 0, 0, 0))
    A = np.asarray(sheet)[:, :, 3] > 0
    moved = 0
    for c in range(cols):
        col = A[:, FW * c:FW * (c + 1)]
        ys, xs = np.nonzero(col)
        if not len(ys):
            continue
        cell = sheet.crop((FW * c, 0, FW * (c + 1), FH))
        # Feet keep their relationship to the foot line — including "floats by N".
        dy = FOOT2 - FOOT
        # Body centre keeps its relationship to the cell centre.
        dx = (FW2 - FW) // 2
        out.alpha_composite(cell, (FW2 * c + dx, dy))
        moved += 1
    man = dict(man, frameW=FW2, frameH=FH2, footY=FOOT2)
    return out, man, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheets', default='web/assets/sprites')
    ap.add_argument('--name', default='oni')
    ap.add_argument('--frame-w', type=int, required=True)
    ap.add_argument('--frame-h', type=int, required=True)
    ap.add_argument('--foot-y', type=int, required=True)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    sd = pathlib.Path(a.sheets)
    man = json.loads((sd / f'{a.name}.json').read_text())
    sheet = Image.open(sd / f'{a.name}.png').convert('RGBA')
    assert sheet.width == man['frameW'] * man['cols'], 'sheet width does not match frameW*cols'

    out, man2, moved = grow(sheet, man, a.frame_w, a.frame_h, a.foot_y)
    print(f"  {man['frameW']}x{man['frameH']} footY {man['footY']}"
          f"  ->  {man2['frameW']}x{man2['frameH']} footY {man2['footY']}")
    print(f'  {moved} cells re-placed, {man["cols"]} columns, indices unchanged')

    # headroom report, because the whole point is the margin
    A = np.asarray(out)[:, :, 3] > 0
    FW2, FOOT2 = man2['frameW'], man2['footY']
    above = below = 0
    for c in range(man2['cols']):
        col = A[:, FW2 * c:FW2 * (c + 1)]
        ys, _ = np.nonzero(col)
        if len(ys):
            above = max(above, FOOT2 - ys.min())
            below = max(below, max(0, ys.max() - FOOT2))
    print(f'  headroom above the foot line: {FOOT2 - above}px   below: {man2["frameH"] - FOOT2 - below}px')
    if a.dry:
        print('  dry run — nothing written')
        return
    out.save(sd / f'{a.name}.png')
    (sd / f'{a.name}.json').write_text(json.dumps(man2, indent=1))
    print(f'  wrote {sd}/{a.name}.png  {out.width}x{out.height}')


def _selfcheck():
    """Art must survive the move byte-for-byte, land on the new foot line, and
    keep a floating cell floating by exactly the same amount."""
    FW, FH, FOOT = 40, 30, 26
    sheet = Image.new('RGBA', (FW * 2, FH), (0, 0, 0, 0))
    planted = Image.new('RGBA', (8, 10), (255, 0, 0, 255))
    floater = Image.new('RGBA', (8, 10), (0, 0, 255, 255))
    sheet.paste(planted, (6, FOOT - 10))            # feet exactly on footY
    sheet.paste(floater, (FW + 6, FOOT - 10 - 5))   # floats 5px above it
    man = dict(frameW=FW, frameH=FH, footY=FOOT, cols=2, frames={'a': 0, 'b': 1}, scale=0.5)

    B = np.asarray(sheet)[:, :, 3] > 0
    b0 = np.nonzero(B[:, :FW].any(1))[0].max()
    b1 = np.nonzero(B[:, FW:].any(1))[0].max()
    gap_before = b0 - b1                       # how far the floater floats

    out, man2, moved = grow(sheet, man, 60, 44, 38)
    assert moved == 2 and man2['frames'] == man['frames'], 'frames{} must not be rewritten'
    assert man2['scale'] == man['scale'], 'scale must not change when the box grows'
    A = np.asarray(out)[:, :, 3] > 0
    a0 = np.nonzero(A[:, :60].any(1))[0].max()
    a1 = np.nonzero(A[:, 60:].any(1))[0].max()
    dy = 38 - FOOT
    assert a0 == b0 + dy, f'planted cell moved {a0 - b0}px, want exactly footY delta {dy}'
    assert a0 - a1 == gap_before, f'floating cell lost its float: {a0 - a1}px, want {gap_before}'
    # counts are the cheapest proof the pixels themselves were not touched
    assert A.sum() == B.sum(), 'opaque pixel count changed — art was altered, not moved'
    print('  selfcheck OK — indices and scale preserved, every cell shifted by exactly the '
          'footY delta, float preserved, pixel count unchanged')


if __name__ == '__main__':
    import sys
    if '--selfcheck' in sys.argv:
        _selfcheck()
    else:
        main()
