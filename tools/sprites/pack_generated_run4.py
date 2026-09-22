#!/usr/bin/env python3
"""Pack the first four cleaned poses from each generated run strip.

The existing sheet is kept intact.  Four cells named run_clean1..4 are
appended (or replaced on a rerun), aligned to the character's established
foot line and scaled to the height of the original run artwork.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "web" / "assets" / "sprites"
GENERATED = Path(__file__).resolve().parent / "generated_run8"
ROSTER = ("executioner", "mizu", "shin", "tsubasa", "ember", "kael")


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    return image.getchannel("A").getbbox()


def strip_cell(strip: Image.Image, index: int, count: int = 8) -> Image.Image:
    """Split strips whose width is not necessarily divisible by cell count."""
    left = round(index * strip.width / count)
    right = round((index + 1) * strip.width / count)
    return strip.crop((left, 0, right, strip.height))


def fit_pose(pose: Image.Image, frame_w: int, frame_h: int,
             target_h: int, foot_y: int) -> Image.Image:
    bbox = alpha_bbox(pose)
    if bbox is None:
        return Image.new("RGBA", (frame_w, frame_h))
    pose = pose.crop(bbox)
    scale = min(target_h / pose.height, (frame_w - 4) / pose.width)
    size = (max(1, round(pose.width * scale)), max(1, round(pose.height * scale)))
    pose = pose.resize(size, Image.Resampling.LANCZOS)

    cell = Image.new("RGBA", (frame_w, frame_h))
    x = (frame_w - pose.width) // 2
    y = min(frame_h - pose.height, foot_y - pose.height)
    cell.alpha_composite(pose, (x, max(0, y)))
    return cell


def pack(name: str) -> None:
    manifest_path = SPRITES / f"{name}.json"
    sheet_path = SPRITES / f"{name}.png"
    strip_path = GENERATED / f"{name}-run8.png"
    manifest = json.loads(manifest_path.read_text())
    sheet = Image.open(sheet_path).convert("RGBA")
    strip = Image.open(strip_path).convert("RGBA")

    fw, fh = manifest["frameW"], manifest["frameH"]
    frames = manifest["frames"]
    run_box = alpha_bbox(sheet.crop((frames["run1"] * fw, 0,
                                     (frames["run1"] + 1) * fw, fh)))
    target_h = (run_box[3] - run_box[1]) if run_box else fh - 12

    first_index = frames.get("run_clean1", manifest["cols"])
    needed_cols = max(manifest["cols"], first_index + 4)
    packed = Image.new("RGBA", (needed_cols * fw, fh))
    packed.paste(sheet, (0, 0))

    for i in range(4):
        cell = fit_pose(strip_cell(strip, i), fw, fh, target_h, manifest["footY"])
        idx = first_index + i
        packed.paste((0, 0, 0, 0), (idx * fw, 0, (idx + 1) * fw, fh))
        packed.alpha_composite(cell, (idx * fw, 0))
        frames[f"run_clean{i + 1}"] = idx

    manifest["cols"] = needed_cols
    packed.save(sheet_path, optimize=True)
    manifest_path.write_text(json.dumps(manifest, separators=(",", ":")) + "\n")
    print(f"{name}: packed run_clean1..4 at {first_index}..{first_index + 3}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", choices=ROSTER)
    args = parser.parse_args()
    for name in args.names or ROSTER:
        pack(name)


if __name__ == "__main__":
    main()
