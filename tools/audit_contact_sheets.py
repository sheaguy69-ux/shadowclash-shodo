#!/usr/bin/env python3
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


COMMITS = ["830ac00", "864162e", "44b1c04", "39306e3", "04a5ea0"]


def show(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], check=True, capture_output=True).stdout


def load(commit, path):
    return Image.open(io.BytesIO(show(commit, path))).convert("RGBA")


def changed_fighters(commit):
    output = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    return sorted(Path(path).stem for path in output if path.startswith("web/assets/sprites/") and path.endswith(".png"))


def fit(cell, width=220, height=220):
    copy = cell.copy()
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (30, 30, 36, 255))
    canvas.alpha_composite(copy, ((width - copy.width) // 2, height - copy.height))
    return canvas


def main(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for commit in COMMITS:
        parent = subprocess.run(["git", "rev-parse", f"{commit}^"], check=True, capture_output=True, text=True).stdout.strip()
        for fighter in changed_fighters(commit):
            manifest_path = f"web/assets/sprites/{fighter}.json"
            png_path = f"web/assets/sprites/{fighter}.png"
            before_manifest = json.loads(show(parent, manifest_path))
            after_manifest = json.loads(show(commit, manifest_path))
            before = load(parent, png_path)
            after = load(commit, png_path)
            frame_width = after_manifest["frameW"]
            frame_height = after_manifest["frameH"]
            index_names = {index: name for name, index in after_manifest["frames"].items()}
            changed = []
            for index in range(after_manifest["cols"]):
                box = (index * frame_width, 0, (index + 1) * frame_width, frame_height)
                if index >= before_manifest["cols"] or ImageChops.difference(before.crop(box), after.crop(box)).getbbox():
                    changed.append(index)
            tile_width, tile_height, label_height = 220, 220, 24
            sheet = Image.new("RGBA", (tile_width * len(changed), (tile_height + label_height) * 2), (18, 18, 24, 255))
            draw = ImageDraw.Draw(sheet)
            for column, index in enumerate(changed):
                box = (index * frame_width, 0, (index + 1) * frame_width, frame_height)
                old_cell = before.crop(box) if index < before_manifest["cols"] else Image.new("RGBA", (frame_width, frame_height))
                new_cell = after.crop(box)
                x = column * tile_width
                sheet.alpha_composite(fit(old_cell), (x, label_height))
                sheet.alpha_composite(fit(new_cell), (x, tile_height + label_height * 2))
                name = index_names.get(index, f"cell_{index}")
                draw.text((x + 5, 5), f"BEFORE {name}", fill="white")
                draw.text((x + 5, tile_height + label_height + 5), f"AFTER {name}", fill="white")
            sheet.save(output_dir / f"{commit}-{fighter}.png")
            print(f"{commit} {fighter}: {len(changed)} changed cells")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) == 2 else "media/audit-contact-sheets-2026-07-16"))
