#!/usr/bin/env python3
"""Erase sub-visible debris specks from packed sheets. NEGATIVE SPACE ONLY.

    python3 tools/sprites/purge_debris.py --dry          # report, change nothing
    python3 tools/sprites/purge_debris.py --apply        # write the sheets

⛔ THE OWNER'S RULE THIS OBEYS (Sep 3 2026): *"erase only the negative space that we don't
need"* — never the ink, never drawn art. So the eligibility test is deliberately narrow and
every condition must hold at once:

  * the pixel belongs to a connected component of at most MAX_PX pixels, and
  * that whole component's MAX alpha is at most MAX_ALPHA — sub-visible, and
  * it sits at least MIN_GAP px clear of the figure (the largest component in the cell).

Anything a viewer could actually see, anything touching the figure, and anything big enough
to be a blade tip, a spark or a dust mote fails at least one of those and is left alone.

WHAT THIS IS ACTUALLY CLEANING. A packing step left a 1px RGB(0,0,0) marker at alpha 9 —
one step above the engine's ink floor of 8 — in the corners of 74 cells across six
fighters, Oni worst at 43. They are invisible in game and they poison every measurement
that reads a bounding box: a single such pixel at (0,64) measured Exile's idle at 216.0px
against a 126.5px target and failed her on the roster gate by 1.7x, and they produced most
of the "cut-off" findings in the Sep-3 audit (29 claimed, exactly 1 real).

VERIFICATION IS PART OF THE RUN, not a separate step. After writing, every pixel at alpha
>= MAX_ALPHA+1 must be byte-identical to before, and each cell's main figure component must
be unchanged. If either check fails the sheets are not written.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import warnings

warnings.filterwarnings("ignore")
import numpy as np
from PIL import Image
from scipy import ndimage as nd

Image.MAX_IMAGE_PIXELS = None

MAX_PX = 4  # a speck this small cannot be a limb, a blade or a spark
MAX_ALPHA = 16  # the engine's ink floor is 8; this is barely above invisible
MIN_GAP = 20  # must be clear of the figure by this much


def eligible(cell: np.ndarray) -> np.ndarray:
    """Boolean mask of debris pixels in one cell. Empty when nothing qualifies."""
    alpha = cell[:, :, 3]
    ink = alpha >= 8
    out = np.zeros(ink.shape, bool)
    if not ink.any():
        return out
    labels, count = nd.label(ink, np.ones((3, 3)))
    if count < 2:
        return out
    sizes = nd.sum(ink, labels, range(1, count + 1))
    main = int(np.argmax(sizes)) + 1
    gap = nd.distance_transform_edt(labels != main)
    for i in range(1, count + 1):
        if i == main or sizes[i - 1] > MAX_PX:
            continue
        sel = labels == i
        if alpha[sel].max() > MAX_ALPHA or gap[sel].min() < MIN_GAP:
            continue
        out |= sel
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry):
        ap.error("pass --dry or --apply")

    grand = 0
    for path in sorted(glob.glob("web/assets/sprites/*.json")):
        name = os.path.basename(path)[:-5]
        meta = json.loads(open(path).read())
        png = f"web/assets/sprites/{name}.png"
        if "frames" not in meta or not os.path.exists(png):
            continue
        before = np.array(Image.open(png).convert("RGBA"))
        after = before.copy()
        fw, cols = meta["frameW"], meta["cols"]
        removed = cells = 0
        for c in range(cols):
            sl = slice(c * fw, (c + 1) * fw)
            mask = eligible(before[:, sl])
            if not mask.any():
                continue
            after[:, sl][mask, 3] = 0
            removed += int(mask.sum())
            cells += 1
        if not removed:
            continue
        grand += removed

        # ---- verification, before anything is written ----
        keep_before = before[:, :, 3] > MAX_ALPHA
        keep_after = after[:, :, 3] > MAX_ALPHA
        assert np.array_equal(keep_before, keep_after), f"{name}: visible ink changed"
        assert np.array_equal(
            before[keep_before], after[keep_before]
        ), f"{name}: a visible pixel was altered"
        for c in range(cols):
            sl = slice(c * fw, (c + 1) * fw)
            for img in (before, after):
                ink = img[:, sl][:, :, 3] >= 8
                if not ink.any():
                    break
            b_ink = before[:, sl][:, :, 3] >= 8
            a_ink = after[:, sl][:, :, 3] >= 8
            if not b_ink.any():
                continue
            lb, nb = nd.label(b_ink, np.ones((3, 3)))
            sb = nd.sum(b_ink, lb, range(1, nb + 1))
            main_b = lb == (int(np.argmax(sb)) + 1)
            la, na = nd.label(a_ink, np.ones((3, 3)))
            sa = nd.sum(a_ink, la, range(1, na + 1))
            main_a = la == (int(np.argmax(sa)) + 1)
            assert np.array_equal(main_b, main_a), f"{name}: cell {c} figure changed"

        print(f"  {name:<12} {removed:4d} debris px across {cells:3d} cells — figure verified intact")
        if args.apply:
            Image.fromarray(after, "RGBA").save(png)

    print(f"\n{'APPLIED' if args.apply else 'DRY RUN'}: {grand} debris pixels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
