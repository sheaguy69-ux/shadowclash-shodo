#!/usr/bin/env python3
import io
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image


COMMITS = [
    "6f5bacf", "830ac00", "8ca9ff9", "70d6597", "9b31e19", "296ac3c",
    "864162e", "44b1c04", "dce49c3", "0d46b0a", "45f2f7c",
]


def git(*args, binary=False):
    result = subprocess.run(["git", *args], check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode()


def show(commit, path, binary=False):
    return git("show", f"{commit}:{path}", binary=binary)


def sheet_version(commit):
    source = show(commit, "web/index.html")
    match = re.search(r"\bSHEET_V\s*=\s*(\d+)", source)
    return int(match.group(1)) if match else None


def changed_files(commit):
    return git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()


def image(commit, path):
    return Image.open(io.BytesIO(show(commit, path, binary=True))).convert("RGBA")


def compare_cells(parent, commit, fighter):
    manifest_path = f"web/assets/sprites/{fighter}.json"
    png_path = f"web/assets/sprites/{fighter}.png"
    before_manifest = json.loads(show(parent, manifest_path))
    after_manifest = json.loads(show(commit, manifest_path))
    before = image(parent, png_path)
    after = image(commit, png_path)
    frame_width = before_manifest["frameW"]
    frame_height = before_manifest["frameH"]
    exact_cells = 0
    visible_cells = 0
    changed_pixels = 0
    visible_changed_pixels = 0
    for index in range(before_manifest["cols"]):
        box = (index * frame_width, 0, (index + 1) * frame_width, frame_height)
        old_pixels = list(before.crop(box).getdata())
        new_pixels = list(after.crop(box).getdata())
        exact = old_pixels == new_pixels
        visible = all(
            old == new or (old[3] == 0 and new[3] == 0)
            for old, new in zip(old_pixels, new_pixels)
        )
        exact_cells += exact
        visible_cells += visible
        for old, new in zip(old_pixels, new_pixels):
            if old != new:
                changed_pixels += 1
                if old[3] != 0 or new[3] != 0:
                    visible_changed_pixels += 1
    expected_size = (
        after_manifest["frameW"] * after_manifest["cols"],
        after_manifest["frameH"],
    )
    indices = list(after_manifest["frames"].values())
    return {
        "fighter": fighter,
        "before_cols": before_manifest["cols"],
        "after_cols": after_manifest["cols"],
        "actual_size": list(after.size),
        "expected_size": list(expected_size),
        "dimensions_ok": after.size == expected_size,
        "indices_ok": bool(indices) and min(indices) >= 0 and max(indices) < after_manifest["cols"],
        "unique_indices": len(indices) == len(set(indices)),
        "exact_untouched_cells": exact_cells,
        "visible_untouched_cells": visible_cells,
        "compared_cells": before_manifest["cols"],
        "changed_pixels": changed_pixels,
        "visible_changed_pixels": visible_changed_pixels,
    }


def audit(commit):
    parent = git("rev-parse", f"{commit}^").strip()
    files = changed_files(commit)
    fighters = sorted({Path(path).stem for path in files if path.startswith("web/assets/sprites/") and path.endswith(".png")})
    before_version = sheet_version(parent)
    after_version = sheet_version(commit)
    return {
        "commit": commit,
        "title": git("show", "-s", "--format=%s", commit).strip(),
        "changed_files": files,
        "sheet_version_before": before_version,
        "sheet_version_after": after_version,
        "sprite_bytes_changed": bool(fighters),
        "sheet_version_bumped": after_version != before_version,
        "sprites": [compare_cells(parent, commit, fighter) for fighter in fighters],
    }


def final_state(commit="HEAD"):
    sprites = []
    for manifest_path in sorted(Path("web/assets/sprites").glob("*.json")):
        manifest = json.loads(show(commit, str(manifest_path)))
        fighter = manifest_path.stem
        sprite = image(commit, f"web/assets/sprites/{fighter}.png")
        indices = list(manifest["frames"].values())
        expected_size = (manifest["frameW"] * manifest["cols"], manifest["frameH"])
        sprites.append({
            "fighter": fighter,
            "actual_size": list(sprite.size),
            "expected_size": list(expected_size),
            "dimensions_ok": sprite.size == expected_size,
            "indices_ok": bool(indices) and min(indices) >= 0 and max(indices) < manifest["cols"],
            "unique_indices": len(indices) == len(set(indices)),
        })
    return {"commit": commit, "sheet_version": sheet_version(commit), "sprites": sprites}


def main():
    report = {"commits": [audit(commit) for commit in COMMITS], "final_state": final_state()}
    output = json.dumps(report, indent=2)
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(output + "\n")
    else:
        print(output)


if __name__ == "__main__":
    main()
