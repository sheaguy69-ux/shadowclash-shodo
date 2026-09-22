#!/usr/bin/env python3
"""Build scale-correct Shodō idle review strips without touching runtime atlases."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "media/shodo-core-review"
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
BOARDS = {
    "oni": "oni-shodo-founders-vigil-idle-8f-v3-codex-review",
    "mokurai": "mokurai-shodo-prayer-mala-idle-8f-v7-safe-margin-review",
    "executioner": "executioner-shodo-iaijutsu-idle-8f-v7-safe-cell-layout-review",
    "exile": "exile-shodo-kusarigama-idle-8f-v5-safe-margin-approved-review",
    "kael": "kael-shodo-idle-8f-v2",
    "tsubasa": "tsubasa-shodo-idle-8f-v4",
    "ember": "ember-shodo-idle-8f-v3",
    "shin": "shin-shodo-idle-owner-model-8f-v6-safe-margin-approved-review",
    "mizu": "mizu-shodo-bo-idle-8f-v1",
}
ANCHOR_BEATS = {"shin": 4}
PREVIEW_SCALE = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_card(path: Path) -> Image.Image:
    """Keep existing alpha; otherwise use the project's 42% corner flood key."""
    source = Image.open(path).convert("RGBA")
    if source.getchannel("A").getextrema()[0] < 255:
        image = source
    else:
        with tempfile.TemporaryDirectory() as tmp:
            keyed = Path(tmp) / "keyed.png"
            subprocess.run([
                "magick", str(path), "-alpha", "set", "-bordercolor", "white", "-border", "1",
                "-fuzz", "42%", "-fill", "none", "-floodfill", "+0+0", "white",
                "-shave", "1x1", str(keyed),
            ], check=True)
            image = Image.open(keyed).convert("RGBA")
    rgba = np.asarray(image).copy()
    alpha = rgba[..., 3] > 12
    band = slice(int(image.height * 0.62), image.height)
    gray = (rgba[band, :, :3].min(2) > 95) & (
        rgba[band, :, :3].max(2).astype(int) - rgba[band, :, :3].min(2) < 44
    )
    alpha[band][gray] = False
    labels, count = ndimage.label(alpha)
    if count:
        sizes = ndimage.sum(alpha, labels, range(1, count + 1))
        main = int(np.argmax(sizes)) + 1
        keep_labels = {main}
        large = {index + 1 for index, size in enumerate(sizes) if size >= float(max(sizes)) * 0.01}
        while True:
            near = ndimage.binary_dilation(np.isin(labels, list(keep_labels)), iterations=20)
            linked = set(np.unique(labels[near])) - {0}
            grown = keep_labels | large | linked
            if grown == keep_labels:
                break
            keep_labels = grown
        keep = np.isin(labels, list(keep_labels))
        rgba[..., 3] = np.where(keep, rgba[..., 3], 0)
        image = Image.fromarray(rgba, "RGBA")
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError(f"no keyed art in {path}")
    return image


def place_at_foot(image: Image.Image, width: int, height: int, foot_y: int) -> Image.Image:
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out.alpha_composite(image, ((width - image.width) // 2, foot_y - image.height))
    return out


def scaled_sequence(fighter: str) -> tuple[list[Image.Image], dict]:
    board = ROOT / "art/shodo-source" / fighter / BOARDS[fighter]
    paths = [board / f"frame-{beat:02d}.png" for beat in range(1, 9)]
    keyed = [key_card(path) for path in paths]
    bounds = [image.getchannel("A").getbbox() for image in keyed]
    union = (min(box[0] for box in bounds), min(box[1] for box in bounds),
             max(box[2] for box in bounds), max(box[3] for box in bounds))
    windows = [image.crop(union) for image in keyed]
    anchor = ANCHOR_BEATS.get(fighter, 1) - 1
    anchor_height = bounds[anchor][3] - bounds[anchor][1]
    factor = TARGETS[fighter] / anchor_height
    scaled = [image.resize((max(1, round(image.width * factor)), max(1, round(image.height * factor))), Image.Resampling.LANCZOS) for image in windows]
    heights = []
    for image in scaled:
        box = image.getchannel("A").getbbox()
        heights.append(0 if box is None else box[3] - box[1])
    report = {
        "fighter": fighter,
        "target_screen_height": TARGETS[fighter],
        "source_board": str(board.relative_to(ROOT)),
        "source_sha256": [sha256(path) for path in paths],
        "anchor_beat": anchor + 1,
        "shared_scale": factor,
        "screen_heights": heights,
        "height_span_px": max(heights) - min(heights),
        "anchor_exact": abs(heights[anchor] - TARGETS[fighter]) <= 0.5,
    }
    return scaled, report


def labeled_strip(fighter: str, frames: list[Image.Image]) -> Image.Image:
    zoomed = [frame.resize((frame.width * PREVIEW_SCALE, frame.height * PREVIEW_SCALE), Image.Resampling.NEAREST) for frame in frames]
    cell_w = max(frame.width for frame in zoomed) + 24
    ground = max(frame.height for frame in zoomed) + 42
    out = Image.new("RGB", (cell_w * 8, ground + 42), "#ded8c8")
    draw = ImageDraw.Draw(out)
    draw.line((0, ground, out.width, ground), fill="#6f1f1a", width=2)
    for index, frame in enumerate(zoomed):
        out.paste(frame, (index * cell_w + (cell_w - frame.width) // 2, ground - frame.height), frame)
        draw.text((index * cell_w + 6, ground + 6), str(index + 1), fill="#211b18")
    draw.text((8, 8), f"{fighter.upper()} — {TARGETS[fighter]:.1f}px canon — one shared scale", fill="#211b18", font=ImageFont.load_default())
    return out


def roster_plate(first_frames: dict[str, Image.Image]) -> Image.Image:
    order = list(TARGETS)
    zoomed = {name: image.resize((image.width * PREVIEW_SCALE, image.height * PREVIEW_SCALE), Image.Resampling.NEAREST) for name, image in first_frames.items()}
    cell_w = max(image.width for image in zoomed.values()) + 24
    ground = max(image.height for image in zoomed.values()) + 44
    out = Image.new("RGB", (cell_w * len(order), ground + 52), "#ded8c8")
    draw = ImageDraw.Draw(out)
    draw.line((0, ground, out.width, ground), fill="#6f1f1a", width=3)
    for index, name in enumerate(order):
        image = zoomed[name]
        x = index * cell_w + (cell_w - image.width) // 2
        out.paste(image, (x, ground - image.height), image)
        draw.text((index * cell_w + 4, ground + 6), f"{name}\n{TARGETS[name]:.1f}px", fill="#211b18")
    draw.text((8, 8), "SHODŌ STORY BIBLE SCALE — 4× REVIEW", fill="#211b18", font=ImageFont.load_default())
    return out


def strip_grid(strips: list[Image.Image]) -> Image.Image:
    width = 1200
    resized = [strip.resize((width, round(strip.height * width / strip.width)), Image.Resampling.LANCZOS) for strip in strips]
    cell_h = max(strip.height for strip in resized)
    out = Image.new("RGB", (width * 3, cell_h * 3), "#ded8c8")
    for index, strip in enumerate(resized):
        out.paste(strip, ((index % 3) * width, (index // 3) * cell_h))
    return out


def self_test() -> None:
    figure = Image.new("RGBA", (8, 20), (20, 20, 20, 255))
    placed = place_at_foot(figure, 30, 40, 35)
    assert placed.getchannel("A").getbbox() == (11, 15, 19, 35)
    assert all(abs(TARGETS[name] - target) < 1e-9 for name, target in TARGETS.items())
    print("SHODO CORE REVIEW SELF-TEST: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    first_frames = {}
    strips = []
    for fighter in TARGETS:
        frames, report = scaled_sequence(fighter)
        first_frames[fighter] = frames[ANCHOR_BEATS.get(fighter, 1) - 1]
        strip = labeled_strip(fighter, frames)
        strip.save(OUT / f"{fighter}-idle-v3.png")
        strips.append(strip)
        reports.append(report)
    roster_plate(first_frames).save(OUT / "roster-scale-v3.png")
    strip_grid(strips).save(OUT / "idle-strips-v3.png")
    (OUT / "measurements-v3.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(OUT / "roster-scale-v3.png")
    for report in reports:
        print(f'{report["fighter"]:<12} target={report["target_screen_height"]:>4.1f}px '
              f'span={report["height_span_px"]:>2}px source={report["source_board"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
