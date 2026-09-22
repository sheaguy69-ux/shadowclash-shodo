#!/usr/bin/env python3
"""Assemble a labeled candidate montage for any Shadow Clash fighter.

Usage:
    python3 tools/sprites/assemble_montage.py <character> <statics_dir> [--sprint f1,f2,...] [--attack f1,f2,...] [--flying f1,f2,...] [--out path]

Defaults per character:
    mizu: sprint-v2 + staff-attack
    shin: sprint-v2 + flyingkick-v2
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

DEFAULTS = {
    "mizu": {
        "sprint_dir": "media/polished-candidates/mizu-i2v/sprint-v2/frames",
        "attack_dir": "media/polished-candidates/mizu-i2v/staff-attack/frames",
        "sprint_frames": ["f_019", "f_025", "f_031", "f_037", "f_049"],
        "attack_frames": ["f_019", "f_031", "f_049", "f_061", "f_073"],
        "frozen_label": "LIGHT/KICK FROZEN",
    },
    "shin": {
        "sprint_dir": "media/polished-candidates/shin-sprint-i2v-v2/frames",
        "flying_dir": "media/polished-candidates/shin-flyingkick-i2v-v2/frames",
        "sprint_frames": ["f_025", "f_050", "f_075", "f_100", "f_121"],
        "flying_frames": ["f_025", "f_050", "f_075", "f_100", "f_121"],
        "frozen_label": "LIGHT/KICK FROZEN",
    },
}

CELL_W, CELL_H = 192, 214
LABEL_H = 28
COLS = 6


def build_cells(args):
    defaults = DEFAULTS.get(args.character, {})
    statics = sorted([n[:-4] for n in os.listdir(args.statics) if n.endswith(".png")])
    cells = []
    for name in statics:
        cells.append((name, os.path.join(args.statics, f"{name}.png")))

    sprint_frames = args.sprint or defaults.get("sprint_frames", [])
    sprint_dir = args.sprint_dir or defaults.get("sprint_dir")
    for f in sprint_frames:
        cells.append((f"sprint-{f}", os.path.join(sprint_dir, f"{f}.png")))

    attack_frames = args.attack or defaults.get("attack_frames", [])
    attack_dir = args.attack_dir or defaults.get("attack_dir")
    for f in attack_frames:
        cells.append((f"staff-{f}", os.path.join(attack_dir, f"{f}.png")))

    flying_frames = args.flying or defaults.get("flying_frames", [])
    flying_dir = args.flying_dir or defaults.get("flying_dir")
    for f in flying_frames:
        cells.append((f"fly-{f}", os.path.join(flying_dir, f"{f}.png")))

    frozen = args.frozen if args.frozen is not None else defaults.get("frozen_label", "")
    if frozen:
        cells.append((frozen, None))

    return cells


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("character")
    parser.add_argument("statics")
    parser.add_argument("--sprint", help="comma-separated frame names")
    parser.add_argument("--attack", help="comma-separated frame names")
    parser.add_argument("--flying", help="comma-separated frame names")
    parser.add_argument("--sprint-dir")
    parser.add_argument("--attack-dir")
    parser.add_argument("--flying-dir")
    parser.add_argument("--frozen", default=None)
    parser.add_argument("--out")
    parser.add_argument("--highlight", help="comma-separated cell labels to mark orange (owner-judge flags)")
    args = parser.parse_args()

    cells = build_cells(args)
    rows = (len(cells) + COLS - 1) // COLS
    while len(cells) < rows * COLS:
        cells.append(("", None))

    out_path = args.out or f"media/polished-candidates/{args.character}/FINAL-candidate-montage.png"
    img = Image.new("RGBA", (COLS * CELL_W, rows * CELL_H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except Exception:
        font = ImageFont.load_default()

    for idx, (label, path) in enumerate(cells):
        cx, cy = idx % COLS, idx // COLS
        x, y = cx * CELL_W, cy * CELL_H
        draw.rectangle([x, y, x + CELL_W, y + CELL_H], fill=(255, 255, 255, 255), outline=(200, 200, 200, 255))

        if path and os.path.exists(path):
            src = Image.open(path).convert("RGBA")
            data = src.getdata()
            new_data = []
            for r, g, b, a in data:
                if r > 240 and g > 240 and b > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append((r, g, b, a))
            src.putdata(new_data)
            bbox = src.getbbox()
            if bbox:
                src = src.crop(bbox)
                avail_w = CELL_W - 8
                avail_h = CELL_H - LABEL_H - 8
                scale = min(avail_w / src.width, avail_h / src.height)
                nw = max(1, int(src.width * scale))
                nh = max(1, int(src.height * scale))
                src = src.resize((nw, nh), Image.Resampling.LANCZOS)
                px = x + (CELL_W - nw) // 2
                py = y + LABEL_H + (avail_h - nh) // 2
                img.paste(src, (px, py), src)

        highlight = args.highlight and label in args.highlight.split(",")
        if label:
            text_fill = (255, 255, 255, 255) if highlight else (0, 0, 0, 255)
            if highlight:
                # Orange pill behind label
                tx, ty = x + 4, y + 4
                bbox = draw.textbbox((tx, ty), label, font=font)
                draw.rectangle([bbox[0] - 2, bbox[1] - 1, bbox[2] + 2, bbox[3] + 1], fill=(255, 140, 0, 255))
            draw.text((x + 4, y + 4), label, fill=text_fill, font=font)

    img.save(out_path)
    print(f"Saved {out_path}: {img.size}, {len([c for c in cells if c[1]])} image cells")


if __name__ == "__main__":
    main()
