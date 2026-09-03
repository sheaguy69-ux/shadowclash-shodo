#!/usr/bin/env python3
"""Refuse a commit that DAMAGES existing sprite art. Runs on the staged sheets.

WHY THIS EXISTS — owner, 2026-09-03: *"you can catch a mistake before it reaches
production, but you can't catch when you're fucking up. Build that type of skill."*

He is right, and the honest fix is not "look harder". Every piece of damage in this
session was found by a deliberate audit AFTERWARDS, never in the moment:

  - an extraction deleted Mizu's and Tsubasa's EYES from every beat
  - a position rule deleted THE STEEL INSIDE TSUBASA'S KUNAI BLADES
  - a matte solve minted ~200 pinholes per cell
  - a chain erase took Exile's whole raised arm

So the check runs on its own, on every commit, whether anyone remembers it or not.

WHAT IT REFUSES
  1. ANY pre-existing cell whose pixels changed. Sheets are append-only: new art is
     appended, old art is never rewritten. A geometry change (frameW/frameH/footY) is
     allowed, but every old cell must survive byte-identical at the shifted anchor.
  2. A NEW cell that is obviously broken: ink touching the canvas edge (a straight
     cut-off), or the runtime keyer eating it alive.

It does NOT judge art. It only asserts that what was already good stays good.

Bypass, for a deliberate repaint the owner has approved:
    ALLOW_ART_REWRITE=1 git commit ...
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "sprites"))
from keyer_emu import keyed_cell  # noqa: E402

EDGE_INK_MAX = 24  # a couple of stray antialias pixels is not a cut-off


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], capture_output=True, cwd=ROOT).stdout


def staged_sheets() -> list[str]:
    names = git("diff", "--cached", "--name-only").decode().split()
    return sorted(
        {Path(n).stem for n in names if n.startswith("web/assets/sprites/") and n.endswith(".png")}
    )


def load(ref: str, fighter: str):
    raw_png = git("show", f"{ref}:web/assets/sprites/{fighter}.png")
    raw_json = git("show", f"{ref}:web/assets/sprites/{fighter}.json")
    if not raw_png or not raw_json:
        return None, None
    return np.array(Image.open(io.BytesIO(raw_png)).convert("RGBA")), json.loads(raw_json)


def main() -> int:
    if os.environ.get("ALLOW_ART_REWRITE"):
        print("  art guard: BYPASSED by ALLOW_ART_REWRITE")
        return 0
    fighters = staged_sheets()
    if not fighters:
        return 0
    problems: list[str] = []
    for fighter in fighters:
        before, meta_before = load("HEAD", fighter)
        after, meta_after = load(":", fighter)
        if after is None:
            continue
        if before is None:
            print(f"  art guard: {fighter} is new, nothing to protect")
            continue

        ofw, ofh = meta_before["frameW"], meta_before["frameH"]
        nfw, nfh = meta_after["frameW"], meta_after["frameH"]
        # a grown window keeps every old cell, re-anchored on footY and centre-x
        dx = (nfw - ofw) // 2
        dy = meta_after["footY"] - meta_before["footY"]
        cols_before = meta_before["cols"]

        modified = []
        for cell in range(cols_before):
            old = before[:, cell * ofw : (cell + 1) * ofw]
            y0, x0 = dy, cell * nfw + dx
            new = after[y0 : y0 + ofh, x0 : x0 + ofw]
            if old.shape != new.shape or not np.array_equal(old, new):
                modified.append(cell)
        if modified:
            shown = ", ".join(str(c) for c in modified[:12])
            more = "" if len(modified) <= 12 else f" (+{len(modified) - 12} more)"
            problems.append(
                f"{fighter}: {len(modified)} EXISTING cell(s) were rewritten — {shown}{more}.\n"
                f"    Sheets are append-only. Append the new art and repoint the key instead."
            )

        for cell in range(cols_before, meta_after["cols"]):
            raw = after[:, cell * nfw : (cell + 1) * nfw]
            keyed = keyed_cell(raw.copy())
            mask = keyed[:, :, 3] >= 8
            if not mask.any():
                problems.append(f"{fighter}: new cell {cell} is EMPTY after the runtime keyer.")
                continue
            eaten = int(((raw[:, :, 3] >= 8) & (keyed[:, :, 3] < 8)).sum())
            if eaten > 0:
                problems.append(
                    f"{fighter}: new cell {cell} loses {eaten}px to the runtime keyer — "
                    f"it will not draw the way it looks on disk."
                )
            edge = int(
                mask[:, 0].sum() + mask[:, -1].sum() + mask[0].sum() + mask[-1].sum()
            )
            if edge > EDGE_INK_MAX:
                problems.append(
                    f"{fighter}: new cell {cell} has {edge}px of ink ON THE CANVAS EDGE — "
                    f"that is a straight cut-off."
                )

        kept = cols_before - len(modified)
        print(
            f"  art guard: {fighter} {kept}/{cols_before} existing cells byte-identical, "
            f"{meta_after['cols'] - cols_before} appended"
        )

    if problems:
        print("\n  ⛔ ART DAMAGE — commit refused:")
        for p in problems:
            print(f"    - {p}")
        print("\n  If this repaint is deliberate and the owner approved it:")
        print("      ALLOW_ART_REWRITE=1 git commit ...")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
