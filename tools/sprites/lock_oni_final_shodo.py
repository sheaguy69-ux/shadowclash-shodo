#!/usr/bin/env python3
"""Keep Oni's runtime on the final-lock v3 Shodo strip only."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image

from export_shodo_only import atomic_json, atomic_png


ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "web/assets/sprites"
MANIFEST = SPRITES / "oni.json"
SHEET = SPRITES / "oni.png"
LOCK_KEYS = ("stand1", "stand2", "stand3", "stand4", "stand5", "stand6", "idle", "idle2")


def verify() -> None:
    manifest = json.loads(MANIFEST.read_text())
    image = Image.open(SHEET).convert("RGBA")
    width, height = manifest["frameW"], manifest["frameH"]
    assert manifest["cols"] == 8
    assert image.size == (width * 8, height)
    assert all(0 <= cell < 8 for cell in manifest["frames"].values())
    assert all(image.crop((i * width, 0, (i + 1) * width, height)).getbbox() for i in range(8))
    for key in ("stand1", "run_clean1", "block", "hurt", "ajump1", "roll_1", "getup"):
        assert key in manifest["frames"], key
    print("ONI FINAL SHODO LOCK: PASS")


def apply() -> None:
    manifest = json.loads(MANIFEST.read_text())
    image = Image.open(SHEET).convert("RGBA")
    width, height = manifest["frameW"], manifest["frameH"]
    source_cells = [manifest["frames"][key] for key in LOCK_KEYS]
    assert len(set(source_cells)) == 8

    locked = Image.new("RGBA", (width * 8, height), (0, 0, 0, 0))
    for beat, cell in enumerate(source_cells):
        art = image.crop((cell * width, 0, (cell + 1) * width, height))
        assert art.getbbox(), f"blank final-lock beat {beat + 1}"
        locked.paste(art, (beat * width, 0))
        assert locked.crop((beat * width, 0, (beat + 1) * width, height)).tobytes() == art.tobytes()

    def beat_for(key: str) -> int:
        if key in LOCK_KEYS:
            return LOCK_KEYS.index(key)
        match = re.search(r"(\d+)$", key)
        return (int(match.group(1)) - 1) % 8 if match else 0

    frames = {key: beat_for(key) for key in manifest["frames"]}
    for prefix in ("run_clean", "owalk", "guard", "ajump", "roll_"):
        frames.update({f"{prefix}{i}": i - 1 for i in range(1, 9)})
    frames.update({"block": 0, "block2": 1, "hurt": 0, "getup": 0})
    frames.update({f"hurt{i}": i - 1 for i in range(2, 9)})
    frames.update({f"getup{i}": i - 1 for i in range(2, 9)})

    manifest["frames"] = frames
    manifest["cols"] = 8
    for field in ("mirror", "footAdj", "handAnchor"):
        manifest.pop(field, None)
    atomic_png(locked, SHEET)
    atomic_json(manifest, MANIFEST)
    verify()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    verify() if args.check else apply()
