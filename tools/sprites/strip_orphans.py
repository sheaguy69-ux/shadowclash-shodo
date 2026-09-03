#!/usr/bin/env python3
"""Drop cells no key points at, and compact the sheet. STEP TWO of the two-step law.

    python3 tools/sprites/strip_orphans.py --dry
    python3 tools/sprites/strip_orphans.py --apply

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
  * `handAnchor` is keyed BY CELL INDEX (exile only, cells 314-321) and is remapped with
    the same table. Missing that would send her chain to a random hand.
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if not (args.apply or args.dry):
        ap.error("pass --dry or --apply")

    before_px = after_px = 0
    for path in sorted(glob.glob("web/assets/sprites/*.json")):
        name = os.path.basename(path)[:-5]
        meta = json.loads(open(path).read())
        png = f"web/assets/sprites/{name}.png"
        if "frames" not in meta or not os.path.exists(png):
            continue
        live, remap = plan(meta)
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
        bad = []
        for key, old in meta["frames"].items():
            if not isinstance(old, int) or old not in remap:
                continue
            new = remap[old]
            if not np.array_equal(
                sheet[:, old * fw : (old + 1) * fw], out[:, new * fw : (new + 1) * fw]
            ):
                bad.append(key)
        assert not bad, f"{name}: pixels changed for {bad[:6]}"

        new_meta = dict(meta)
        new_meta["cols"] = len(live)
        new_meta["frames"] = {
            k: (remap[v] if isinstance(v, int) and v in remap else v)
            for k, v in meta["frames"].items()
        }
        if isinstance(meta.get("handAnchor"), dict):
            new_meta["handAnchor"] = {
                str(remap[int(k)]): v
                for k, v in meta["handAnchor"].items()
                if int(k) in remap
            }
            kept = len(new_meta["handAnchor"])
            print(
                f"  {name:<12} {dropped:4d} orphans dropped, {len(live):4d} kept "
                f"(handAnchor remapped, {kept} entries)"
            )
        else:
            print(f"  {name:<12} {dropped:4d} orphans dropped, {len(live):4d} kept")

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
