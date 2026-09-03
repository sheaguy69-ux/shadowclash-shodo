#!/usr/bin/env python3
"""Fail when the standalone Shodō roster is undersized or missing core art."""

from __future__ import annotations

import json
from pathlib import Path

import re
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent / "sprites"))
from keyer_emu import keyed_cell


ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "web/assets/sprites"
TARGETS = {
    "oni": 87.5,
    "mokurai": 75.0,
    "executioner": 72.5,
    "exile": 72.3,
    "kael": 70.0,
    "tsubasa": 69.6,
    "ember": 69.3,
    "shin": 66.6,
    "mizu": 62.4,
}
DISPLAY_SCALE = 1.75
NEUTRAL_KEYS = ("xidle1", "stand1", "idle", "idle1", "canon_idle")
CORE_ROUTES = {
    "neutral": NEUTRAL_KEYS,
    "run": ("run_clean1", "owalk1", "brun1"),
    "block": ("block", "xblock", "canon_guard"),
    "hurt": ("hurt", "xhurt1", "bhurt1", "canon_hit"),
    "jump": ("jump", "jump1", "ajump1", "xjump1", "bjump1"),
    "dodge": ("roll", "roll_1", "slide1", "mroll1"),
    "recover": ("getup", "getup1", "bgetup1"),
}
PROHIBITED_PREFIXES = ("f2_", "hb", "gk")
TOLERANCE_PX = 0.5


def first_present(frames: dict[str, int], keys: tuple[str, ...]) -> str | None:
    return next((key for key in keys if key in frames), None)


def _cell_height(manifest: dict, image: Image.Image, cell: int) -> float:
    """Head-top to footY for the FIGURE, measured the way the engine draws it.

    ⛔ THREE BUGS LIVED IN THE ONE LINE THIS REPLACES, and all three read as "the art is
    the wrong size" when the art was fine:

    1. It used the FILE's alpha. The engine keys at draw time, so file alpha lies; every
       sprite check in this repo has to go through keyed_cell first.
    2. It used `getbbox()`, which is alpha > 0 over the WHOLE cell, so any stray speck set
       the top. Exile carries a single 1px pixel at (0, 64) on xidle1-5 — her figure is at
       y180-334 — and that one pixel measured her at 216.0px against a 126.5px target, a
       1.7x "failure" that was pure junk. Measuring the largest component instead puts her
       at 126.5, exactly on target.
    3. It measured whichever neutral key came first alphabetically. Shin's xidle1 is a
       CROUCHED beat of his breathing cycle (136 cell px) while his standing beats are 185
       and 196, so he was graded on a crouch and read 82.1 against 116.5.
    """
    width, height = manifest["frameW"], manifest["frameH"]
    cropped = np.array(image.crop((cell * width, 0, (cell + 1) * width, height)))
    keyed = keyed_cell(cropped)
    mask = keyed[:, :, 3] >= 8
    if not mask.any():
        return 0.0
    labels, count = nd.label(mask, np.ones((3, 3)))
    if count > 1:
        sizes = nd.sum(mask, labels, range(1, count + 1))
        mask = labels == (int(np.argmax(sizes)) + 1)
    rows = np.nonzero(mask)[0]
    return (manifest["footY"] - rows.min()) * manifest["scale"] * DISPLAY_SCALE


CROUCH_MARGIN = 0.15


def neutral_height(manifest: dict, image: Image.Image, key: str) -> float:
    """The fighter STANDING.

    Normally the first neutral beat IS the standing pose, and that is what the canon
    numbers were taken from — so use it. Shin is the exception: his xidle1 is the CROUCHED
    beat of a breathing cycle at 136 cell px while his standing beats are 185 and 196, so
    grading him on it read 82.1px against a 116.5px target. When the row's tallest beat
    towers over the first by more than CROUCH_MARGIN, the first beat is a crouch and the
    tallest is the standing pose. Taking the tallest unconditionally is wrong the other
    way: it picks up a lift or a stretch beat and pushed Mokurai and Ember over.
    """
    frames = manifest["frames"]
    stem = re.sub(r"\d+$", "", key)
    family = [k for k in frames if re.sub(r"\d+$", "", k) == stem] or [key]
    first = _cell_height(manifest, image, frames[key])
    tallest = max(_cell_height(manifest, image, frames[k]) for k in family)
    return tallest if first and tallest > first * (1 + CROUCH_MARGIN) else first


def main() -> int:
    failures = 0
    for fighter, base_target in TARGETS.items():
        target = base_target * DISPLAY_SCALE
        manifest = json.loads((SPRITES / f"{fighter}.json").read_text())
        frames = manifest["frames"]
        neutral = first_present(frames, NEUTRAL_KEYS)
        missing = [name for name, keys in CORE_ROUTES.items() if first_present(frames, keys) is None]
        prohibited = sorted(key for key in frames if key.startswith(PROHIBITED_PREFIXES))
        measured = None
        if neutral is not None:
            with Image.open(SPRITES / f"{fighter}.png") as image:
                measured = neutral_height(manifest, image.convert("RGBA"), neutral)
        # ⛔ A 0.5px tolerance was TIGHTER THAN ONE SOURCE PIXEL. One cell pixel lands on
        # screen as scale * DISPLAY_SCALE px (0.60 for shin, 0.64 for tsubasa), so art that
        # is exactly right still failed by a rounding step it cannot express.
        tol = max(TOLERANCE_PX, manifest["scale"] * DISPLAY_SCALE)
        size_ok = measured is not None and abs(measured - target) <= tol
        failures += int(not size_ok) + len(missing) + len(prohibited)
        shown = "missing" if measured is None else f"{measured:.1f}px"
        notes = []
        if not size_ok:
            notes.append(f"target {target:.1f}px (off {measured - target:+.1f}, tol {tol:.2f})")
        if missing:
            notes.append("missing " + ",".join(missing))
        if prohibited:
            notes.append("prohibited " + ",".join(prohibited[:5]))
        print(f"{fighter:<12} neutral={neutral or '-':<10} height={shown:<8} " + ("PASS" if not notes else "FAIL " + "; ".join(notes)))

    if failures:
        print(f"SHODO ROSTER: {failures} failure(s)")
        return 1
    print("SHODO ROSTER: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
