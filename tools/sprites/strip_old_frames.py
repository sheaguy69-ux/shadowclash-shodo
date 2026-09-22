#!/usr/bin/env python3
"""Delete a fighter's superseded frames COMPLETELY — the history keys and the cells.

Owner order, Aug 21 2026: "delete all old frames completely" — the same order that
drove SHEET_V 575, and the append-only law is overridden for dead cells by the same
ruling. Git holds every prior sheet.

WHAT COUNTS AS OLD. A packing run keeps the cell it superseded reachable under a
history key (`<name>_v575`, `<name>_v560_3`, `<name>_old`), so nothing is lost while
the new art is being judged. Those keys are the ONLY thing holding that art on the
sheet — once the replacement is accepted they are the old data, and they go with it.

⛔ TWO STEPS, NEVER ONE. The replacement must already be packed and the live key
already repointed BEFORE anything is stripped; a cell that is still some move's only
picture is not an orphan, it is that move. So this removes a cell only when ZERO live
keys reference it, and it says how many of each it found rather than reporting the
order as done.

⛔ REMAP EVERYTHING KEYED BY CELL INDEX, not just `frames`. Three sheets carry a
second index-keyed map — oni/mokurai `mirror`, executioner/mizu `footAdj`, exile
`handAnchor`. Renumbering `frames` and leaving those behind silently attaches one
cell's flags to a different drawing.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "web/assets/sprites"
HISTORY = re.compile(r"_v\d{3}(_\d+)?$|_old$")
INDEX_KEYED = ("mirror", "footAdj", "handAnchor")


def plan(who: str):
    man = json.loads((SPRITES / f"{who}.json").read_text())
    frames = man["frames"]
    history = sorted(k for k in frames if HISTORY.search(k))
    live = {k: v for k, v in frames.items() if k not in history}
    keep = sorted(set(live.values()))
    drop = [i for i in range(man["cols"]) if i not in set(keep)]
    # A history key whose cell some LIVE key still uses frees nothing — the key goes,
    # the picture stays. Reported separately so the count is never mistaken for the art.
    shared = sorted({frames[k] for k in history} & set(keep))
    return man, frames, history, live, keep, drop, shared


def strip(who: str, apply: bool):
    man, frames, history, live, keep, drop, shared = plan(who)
    old_cols, fw, fh = man["cols"], man["frameW"], man["frameH"]
    print(f"{who}: {old_cols} cells, {len(frames)} keys")
    print(f"  history keys to delete : {len(history)}")
    print(f"  cells they alone hold  : {len(drop)}")
    print(f"  cells shared with live : {len(shared)} (key goes, picture stays)")
    print(f"  cells after strip      : {len(keep)}")
    if not apply:
        return
    if not drop:
        # ⛔ A HISTORY KEY IS STALE DATA EVEN WHEN IT FREES NO PIXELS. This used to
        # return here, so shin's `idle_v335` — which shares its cell with the live
        # `idle` — survived every strip and stayed in the manifest forever. The key is
        # the thing being deleted; the cell it happens to share is not a reason to keep
        # the name. No atlas rewrite is needed in this case, only the manifest.
        if history:
            for k in history:
                del frames[k]
            (SPRITES / f"{who}.json").write_text(json.dumps(man, indent=1) + "\n")
            print(f"  STRIPPED: {len(history)} history key(s) deleted "
                  f"({', '.join(history)}); no cell freed, atlas untouched")
        else:
            print("  nothing to strip — every cell is referenced")
        return

    remap = {old: new for new, old in enumerate(keep)}
    old_img = Image.open(SPRITES / f"{who}.png").convert("RGBA")
    assert old_img.size == (old_cols * fw, fh), f"{who}.png is not {old_cols}x1 cells"
    out = Image.new("RGBA", (len(keep) * fw, fh))
    for old, new in remap.items():
        out.paste(old_img.crop((old * fw, 0, (old + 1) * fw, fh)), (new * fw, 0))

    # ⛔ PER-KEY BYTE IDENTITY, not per-index. The whole point of a renumber is that
    # indices move, so comparing index to index proves nothing — every LIVE key must
    # still resolve to exactly the pixels it resolved to before.
    a, b = np.array(out), np.array(old_img)
    for k, old in live.items():
        new = remap[old]
        assert np.array_equal(a[:, new * fw:(new + 1) * fw],
                              b[:, old * fw:(old + 1) * fw]), f"{who}: {k} changed"

    man["frames"] = {k: remap[v] for k, v in live.items()}
    for field in INDEX_KEYED:
        if field in man:
            src = man[field]
            items = enumerate(src) if isinstance(src, list) else ((int(i), v) for i, v in src.items())
            man[field] = {str(remap[i]): v for i, v in items if i in remap}
    man["cols"] = len(keep)

    assert len(man["frames"]) == len(live)
    assert max(man["frames"].values()) == len(keep) - 1
    assert set(man["frames"].values()) == set(range(len(keep))), "renumber left a hole"
    out.save(SPRITES / f"{who}.png", optimize=True)
    (SPRITES / f"{who}.json").write_text(json.dumps(man, indent=1) + "\n")
    print(f"  STRIPPED: {old_cols} -> {len(keep)} cells, "
          f"{len(history)} history keys deleted, {len(live)} live keys re-pointed, "
          f"every one byte-identical")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fighter", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    for who in a.fighter:
        strip(who, a.apply)


if __name__ == "__main__":
    main()
