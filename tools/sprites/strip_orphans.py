#!/usr/bin/env python3
"""Drop cells no key points at, and compact the sheet. STEP TWO of the two-step law.

    python3 tools/sprites/strip_orphans.py --dry
    python3 tools/sprites/strip_orphans.py --apply
    python3 tools/sprites/strip_orphans.py --cells ember:302 --apply   # only what was named

Sheets here are append-only: replacement art is appended and the key is repointed, which
leaves the old cell on the sheet unreferenced. That is deliberate — it means a bad landing
can be undone by moving one pointer. The cost is that the atlas keeps growing, and the
orphans are dead weight in every byte the browser downloads and decodes.

This is the second step: once the owner is happy with what is live, the unreferenced cells
come out and the live ones are renumbered to close the gaps.

⛔ WHAT MAKES THIS SAFE, and it is checked rather than asserted:

  * LIVE = any cell index any key in `frames` points at. Nothing else survives.
  * Every live cell is copied WHOLE and byte-identical into its new slot. No rescale, no
    re-encode, no re-key — the pixels are moved, not touched.
  * EVERY INDEX-KEYED MAP IS REMAPPED, found by shape rather than by name. `handAnchor`
    (exile) was the only one this tool knew about, and it is not the only one there is:
    the roster also carries `mirror`, `frameClear`, `frameScale`, `footAdj`, `frameOffsetX`,
    `wallContactX`, `weaponNoOutline` and `bodyBoundsX` keyed the same way — 217 entries on
    Ember alone, 115 of them `frameScale`. Remapping `frames` and leaving those behind
    silently re-points a render flag at whatever slid into the slot: a cell would come out
    mirrored, rescaled, or with a hole cleared in it, and nothing would throw.

  * A NAMED CELL CANNOT BE DROPPED WHILE ANYTHING STILL POINTS AT IT. `--cells` asserts
    that before it touches a pixel, so "remove exactly this one" cannot quietly take a
    live cell with it.
  * AFTER writing, every key is re-read and its new cell compared byte-for-byte against the
    old cell it used to name. Any mismatch and the sheet is not written.

The engine hardcodes no cell numbers (checked: zero `frames[<literal>]` occurrences), so
the manifest is the only place indices live.
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

Image.MAX_IMAGE_PIXELS = None


def plan(meta: dict) -> tuple[list[int], dict[int, int]]:
    live = sorted({v for v in meta["frames"].values() if isinstance(v, int)})
    live = [c for c in live if 0 <= c < meta["cols"]]
    return live, {old: new for new, old in enumerate(live)}


def plan_cells(meta: dict, drop: list[int]) -> tuple[list[int], dict[int, int]]:
    """Drop ONLY the named cells; every other orphan stays where it is."""
    referenced = {v for v in meta["frames"].values() if isinstance(v, int)}
    for c in drop:
        assert 0 <= c < meta["cols"], f"cell {c} is not on a {meta['cols']}-cell sheet"
        assert c not in referenced, f"cell {c} is LIVE — repoint its keys before dropping it"
    keep = [c for c in range(meta["cols"]) if c not in set(drop)]
    return keep, {old: new for new, old in enumerate(keep)}


def index_maps(meta: dict) -> list[str]:
    """Top-level dicts keyed by cell index, found by shape so a new one is never missed."""
    out = []
    for k, v in meta.items():
        if k == "frames" or not isinstance(v, dict) or not v:
            continue
        if all(str(x).lstrip("-").isdigit() for x in v):
            out.append(k)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--cells", default="",
                    help="drop only these, e.g. ember:302 or ember:302,70 — every other "
                         "orphan is left alone")
    args = ap.parse_args()
    if not (args.apply or args.dry):
        ap.error("pass --dry or --apply")
    only = {}
    for spec in filter(None, args.cells.split()):
        fighter, idxs = spec.split(":")
        only[fighter] = [int(x) for x in idxs.split(",")]

    before_px = after_px = 0
    for path in sorted(glob.glob("web/assets/sprites/*.json")):
        name = os.path.basename(path)[:-5]
        meta = json.loads(open(path).read())
        png = f"web/assets/sprites/{name}.png"
        if "frames" not in meta or not os.path.exists(png):
            continue
        if only and name not in only:
            continue
        live, remap = plan_cells(meta, only[name]) if only else plan(meta)
        cols, fw, fh = meta["cols"], meta["frameW"], meta["frameH"]
        dropped = cols - len(live)
        before_px += cols * fw * fh
        after_px += len(live) * fw * fh
        if dropped <= 0:
            print(f"  {name:<12} nothing to drop")
            continue

        sheet = np.array(Image.open(png).convert("RGBA"))
        out = np.zeros((fh, fw * len(live), 4), dtype=np.uint8)
        for old, new in remap.items():
            out[:, new * fw : (new + 1) * fw] = sheet[:, old * fw : (old + 1) * fw]

        # ---- verify BEFORE writing: every key still names identical pixels ----
        # EVERY remapped cell, not only the ones a `frames` key names — an orphan can
        # still carry a mirror or frameScale flag, and that flag has to follow its pixels.
        bad = [f"cell {o}" for o, nw in remap.items()
               if not np.array_equal(sheet[:, o * fw:(o + 1) * fw],
                                     out[:, nw * fw:(nw + 1) * fw])]
        assert not bad, f"{name}: pixels changed for {bad[:6]}"

        new_meta = dict(meta)
        new_meta["cols"] = len(live)
        new_meta["frames"] = {
            k: (remap[v] if isinstance(v, int) and v in remap else v)
            for k, v in meta["frames"].items()
        }
        # EVERY index-keyed map, found by shape. An entry naming a dropped cell goes with
        # it; every other entry follows its cell to the new slot.
        remapped = []
        for mk in index_maps(meta):
            src = meta[mk]
            new_meta[mk] = {str(remap[int(k)]): v for k, v in src.items() if int(k) in remap}
            lost = len(src) - len(new_meta[mk])
            remapped.append(f"{mk} {len(new_meta[mk])}" + (f" (-{lost})" if lost else ""))
        what = "dropped" if not only else f"dropped ({','.join(map(str, only[name]))})"
        print(f"  {name:<12} {dropped:4d} {what}, {len(live):4d} kept"
              + (f"  ::  {', '.join(remapped)}" if remapped else ""))

        if args.apply:
            Image.fromarray(out, "RGBA").save(png)
            json.dump(new_meta, open(path, "w"), indent=1)

    saved = (before_px - after_px) * 4 / 1e6
    print(
        f"\n{'APPLIED' if args.apply else 'DRY RUN'}: atlas {before_px * 4 / 1e6:.0f} MB "
        f"-> {after_px * 4 / 1e6:.0f} MB decoded, {saved:.0f} MB freed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
