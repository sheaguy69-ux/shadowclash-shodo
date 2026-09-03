#!/usr/bin/env python3
"""Shorten a fighter's ANKLE so his standing height matches canon. Body and feet untouched.

    python3 tools/sprites/shorten_ankle.py --selftest
    python3 tools/sprites/shorten_ankle.py --fighter shin --keys xidle4,xidle5 \
        --band 304:320 --shrink 3 --dry

⛔ WHY THIS EXISTS instead of a whole-fighter rescale — owner ruling, 2026-09-03:
*"he do stand too tall ... edit his ankles, angle should be shorter, make his ankle short
enough that matches his supposed height."*

The two obvious fixes were both wrong. Moving canon rewrites the target to match the art.
Dropping `scale` resamples all 141 cells — every clean frame gets softer to fix two beats.
Shin's own standing poses elsewhere (`getup4`, `kpush5`) already measure 193 footY-px, dead
on canon; only the peak of his breathing cycle towers at 196. So the defect is local and the
repair is local: take the 3px out of the ankle, where a standing figure's height actually
lives, and leave the rest of him alone.

HOW THE CELL IS REBUILT — three regions, only the middle one is resampled:

    y < band.start        BODY   copied byte-identical, translated DOWN by `shrink`
    band.start..band.end  ANKLE  resampled to (height - shrink) rows, bottom-anchored
    y >= band.end         FOOT   copied byte-identical, NOT MOVED — he stays planted

The foot never moves, so footY stays valid and he does not float or sink. The body is not
scaled, so his head, mask, blade and proportions are the same pixels they were.

Sheets here are APPEND-ONLY: the edited cells are appended and the keys repointed, which
leaves the originals on the sheet for `strip_orphans.py` to remove once the owner is happy.
Nothing existing is rewritten, so `check_no_art_damage.py` passes without a bypass.

VERIFICATION RUNS BEFORE ANYTHING IS WRITTEN, on every cell:
  * the rows the body is shifted into must be EMPTY first — nothing is pushed off the top
  * body and foot regions byte-identical to the source
  * the keyed footY-height dropped by EXACTLY `shrink`
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
from PIL import Image
from scipy import ndimage as nd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keyer_emu import keyed_cell

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "web/assets/sprites"


def vresize(band: np.ndarray, rows: int) -> np.ndarray:
    """Vertical-only resize through premultiplied alpha.

    A naive RGBA resize drags the transparent pixels' colour into the ink fringe and the
    brush edge goes muddy. Multiply by alpha, resize in float, divide back out.
    """
    f = band.astype(np.float64)
    a = f[:, :, 3:4] / 255.0
    pm = np.concatenate([f[:, :, :3] * a, f[:, :, 3:4]], axis=2)
    out = np.stack(
        [
            np.asarray(
                Image.fromarray(pm[:, :, c].astype(np.float32), "F").resize(
                    (band.shape[1], rows), Image.LANCZOS
                )
            )
            for c in range(4)
        ],
        axis=2,
    )
    oa = np.clip(out[:, :, 3:4], 0, 255)
    rgb = np.divide(out[:, :, :3], oa / 255.0, out=np.zeros_like(out[:, :, :3]), where=oa > 0.5)
    return np.clip(np.concatenate([rgb, oa], axis=2), 0, 255).astype(np.uint8)


def shorten(cell: np.ndarray, y0: int, y1: int, shrink: int) -> np.ndarray:
    """Rebuild one cell with the ankle band [y0, y1) shortened by `shrink` rows."""
    assert 0 < shrink < (y1 - y0), "shrink must fit inside the band"
    assert not (cell[:shrink, :, 3] >= 8).any(), "ink in the rows the body would shift into"
    out = np.zeros_like(cell)
    out[shrink : y0 + shrink] = cell[:y0]
    out[y0 + shrink : y1] = vresize(cell[y0:y1], y1 - y0 - shrink)
    out[y1:] = cell[y1:]
    return out


def foot_height(cell: np.ndarray, foot_y: int) -> int:
    """footY to the top of the FIGURE, measured the way check_shodo_roster.py does."""
    keyed = keyed_cell(cell.copy())
    mask = keyed[:, :, 3] >= 8
    if not mask.any():
        return 0
    labels, count = nd.label(mask, np.ones((3, 3)))
    if count > 1:
        sizes = nd.sum(mask, labels, range(1, count + 1))
        mask = labels == (int(np.argmax(sizes)) + 1)
    return foot_y - int(np.nonzero(mask)[0].min())


def selftest() -> int:
    """Analytic figure: 40px body, a narrow 16px ankle, a wide foot. Shrink must be exact."""
    cell = np.zeros((100, 60, 4), np.uint8)
    cell[20:60, 20:40] = (30, 30, 30, 255)  # body
    cell[60:76, 26:34] = (30, 30, 30, 255)  # ankle band y60..75
    cell[76:90, 14:46] = (30, 30, 30, 255)  # foot
    out = shorten(cell, 60, 76, 3)

    assert np.array_equal(out[76:], cell[76:]), "foot moved"
    assert np.array_equal(out[23:63], cell[20:60]), "body was altered, not just translated"
    top_before = int(np.nonzero(cell[:, :, 3] >= 8)[0].min())
    top_after = int(np.nonzero(out[:, :, 3] >= 8)[0].min())
    assert top_after - top_before == 3, f"height fell by {top_after - top_before}, want 3"
    assert (out[63:76, :, 3] >= 8).any(), "the ankle vanished"
    ankle_x = np.nonzero(out[68, :, 3] >= 8)[0]
    assert 24 <= ankle_x.min() <= 28 and 32 <= ankle_x.max() <= 36, "ankle changed width"

    # a shrink that would push ink off the top must be refused, not silently clipped
    tall = np.zeros((100, 60, 4), np.uint8)
    tall[0:60, 20:40] = (30, 30, 30, 255)
    tall[60:76, 26:34] = (30, 30, 30, 255)
    try:
        shorten(tall, 60, 76, 3)
    except AssertionError:
        pass
    else:
        raise AssertionError("guard did not fire on ink at the top edge")

    print("selftest OK — foot planted, body translated not scaled, height exact, guard fires")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fighter")
    ap.add_argument("--keys", help="comma-separated frame keys to repoint")
    ap.add_argument("--band", help="ankle rows as START:END, END exclusive (first foot row)")
    ap.add_argument("--shrink", type=int, default=0)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.apply or args.dry):
        ap.error("pass --dry or --apply")
    for need in ("fighter", "keys", "band"):
        if not getattr(args, need):
            ap.error(f"--{need} is required")

    y0, y1 = (int(v) for v in args.band.split(":"))
    path = SPRITES / f"{args.fighter}.json"
    meta = json.loads(path.read_text())
    fw, foot_y, cols = meta["frameW"], meta["footY"], meta["cols"]
    sheet = np.array(Image.open(SPRITES / f"{args.fighter}.png").convert("RGBA"))
    keys = args.keys.split(",")

    new_cells, repoint = [], {}
    for key in keys:
        src = meta["frames"][key]
        cell = sheet[:, src * fw : (src + 1) * fw]
        before = foot_height(cell, foot_y)
        out = shorten(cell, y0, y1, args.shrink)
        after = foot_height(out, foot_y)
        assert np.array_equal(out[y1:], cell[y1:]), f"{key}: the foot moved"
        assert np.array_equal(
            out[args.shrink : y0 + args.shrink], cell[:y0]
        ), f"{key}: the body was altered"
        assert after == before - args.shrink, f"{key}: height {before}->{after}, want -{args.shrink}"
        dst = cols + len(new_cells)
        new_cells.append(out)
        repoint[key] = dst
        px = meta["scale"] * 1.75
        print(
            f"  {key:<10} cell {src:>3} -> {dst:>3}   footH {before} -> {after}   "
            f"screen {before * px:.2f} -> {after * px:.2f}px"
        )

    if not args.apply:
        print("\nDRY RUN — nothing written")
        return 0

    grown = np.zeros((sheet.shape[0], fw * (cols + len(new_cells)), 4), np.uint8)
    grown[:, : sheet.shape[1]] = sheet
    for i, cell in enumerate(new_cells):
        grown[:, (cols + i) * fw : (cols + i + 1) * fw] = cell
    assert np.array_equal(grown[:, : sheet.shape[1]], sheet), "existing cells were disturbed"

    meta["cols"] = cols + len(new_cells)
    meta["frames"].update(repoint)
    Image.fromarray(grown, "RGBA").save(SPRITES / f"{args.fighter}.png")
    path.write_text(json.dumps(meta, indent=1))
    print(f"\nAPPLIED — {len(new_cells)} cells appended, {len(repoint)} keys repointed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
